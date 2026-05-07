import json
import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


MARKER_RE = re.compile(r"Screenshot-\[(?:(\d{2}):)?(\d{2}):(\d{2})\]")
VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm")


def find_candidates(cwd: Path, suffixes: Sequence[str]) -> List[Path]:
    matches: List[Path] = []
    for suffix in suffixes:
        matches.extend(sorted(path for path in cwd.glob(f"*{suffix}") if path.is_file()))
    return matches


def choose_markdown_file(cwd: Path) -> Path:
    candidates = [path for path in sorted(cwd.glob("*.md")) if path.is_file()]
    if not candidates:
        raise RuntimeError("当前目录没有找到 Markdown 文件，请先生成带 Screenshot 占位符的 .md 文件。")

    preferred = [path for path in candidates if "_with_screenshots" not in path.stem]
    chosen = preferred[0] if preferred else candidates[0]
    if len(candidates) > 1:
        logging.info("发现多个 Markdown 文件，使用：%s", chosen.name)
    return chosen


def choose_video_file(cwd: Path, stem_hint: str) -> Optional[Path]:
    candidates = find_candidates(cwd, VIDEO_EXTS)
    if not candidates:
        return None

    exact_match = next((path for path in candidates if path.stem == stem_hint), None)
    if exact_match:
        return exact_match

    simplified_hint = stem_hint.replace("_notes", "").replace("_with_screenshots", "")
    fuzzy_match = next((path for path in candidates if path.stem == simplified_hint), None)
    if fuzzy_match:
        return fuzzy_match

    return candidates[0]


def parse_marker_seconds(marker: str) -> int:
    match = MARKER_RE.fullmatch(marker)
    if not match:
        raise ValueError(f"无法解析截图占位符：{marker}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def collect_markers(markdown: str) -> List[str]:
    return [match.group(0) for match in MARKER_RE.finditer(markdown)]


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("系统中未找到 ffmpeg，无法生成截图。")


def get_video_duration_seconds(video_path: Path) -> Optional[float]:
    if shutil.which("ffprobe") is None:
        return None

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def normalize_capture_second(timestamp_seconds: int, duration_seconds: Optional[float]) -> float:
    if duration_seconds is None:
        return float(timestamp_seconds)
    if duration_seconds <= 0:
        return 0.0
    # When a marker lands at the end of a short or low-fps video, step back enough to reliably hit the final decodable frame.
    return min(float(timestamp_seconds), max(duration_seconds - 1.0, 0.0))


def capture_frame(video_path: Path, output_path: Path, timestamp_seconds: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(timestamp_seconds),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg 截图失败")


def replacement_image_path(seconds: int) -> Tuple[str, Path]:
    file_name = f"screenshot_{seconds:05d}.jpg"
    return f"assets/{file_name}", Path("assets") / file_name


def replace_markers(markdown: str, video_path: Path, assets_dir: Path) -> Tuple[str, List[str], List[str]]:
    generated_images: List[str] = []
    failures: List[str] = []
    seen: dict[str, str] = {}
    duration_seconds = get_video_duration_seconds(video_path)

    def _replace(match: re.Match[str]) -> str:
        marker = match.group(0)
        if marker in seen:
            return seen[marker]

        seconds = parse_marker_seconds(marker)
        relative_path, image_path_relative = replacement_image_path(seconds)
        output_path = assets_dir / image_path_relative.name
        try:
            capture_frame(video_path, output_path, normalize_capture_second(seconds, duration_seconds))
            replacement = f"![screenshot]({relative_path})"
            seen[marker] = replacement
            generated_images.append(str(output_path))
            return replacement
        except Exception as exc:
            logging.warning("截图失败 %s: %s", marker, exc)
            failures.append(f"{marker}: {exc}")
            return marker

    return MARKER_RE.sub(_replace, markdown), generated_images, failures


def write_output_markdown(source_path: Path, markdown: str) -> Path:
    output_path = source_path.with_name(f"{source_path.stem}_with_screenshots.md")
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    cwd = Path.cwd()
    md_path = choose_markdown_file(cwd)
    markdown = md_path.read_text(encoding="utf-8")
    markers = collect_markers(markdown)

    if not markers:
        print(
            json.dumps(
                {
                    "markdown": str(md_path),
                    "output": str(md_path),
                    "video": None,
                    "generated_images": [],
                    "replaced_markers": 0,
                    "failures": [],
                    "note": "Markdown 中未发现 Screenshot 占位符，无需处理。",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    video_path = choose_video_file(cwd, md_path.stem)
    if video_path is None:
        print(
            json.dumps(
                {
                    "markdown": str(md_path),
                    "output": str(md_path),
                    "video": None,
                    "generated_images": [],
                    "replaced_markers": 0,
                    "failures": [],
                    "note": "未找到视频文件，已保留原始 Screenshot 占位符。",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    ensure_ffmpeg()
    output_markdown, generated_images, failures = replace_markers(markdown, video_path, cwd / "assets")
    output_path = write_output_markdown(md_path, output_markdown)

    print(
        json.dumps(
            {
                "markdown": str(md_path),
                "output": str(output_path),
                "video": str(video_path),
                "generated_images": generated_images,
                "replaced_markers": len(generated_images),
                "failures": failures,
                "note": "已生成图文 Markdown。" if not failures else "部分截图失败，失败位置保留原占位符。",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
