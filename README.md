# video-subtitle-markdown

一个给 Codex 使用的 skill：当用户提供视频文件和 `.srt` 字幕文件时，把内容整理成带本地截图的图文 Markdown 成品。

## 功能

- 读取 `.srt` 字幕并整理成 Markdown 笔记
- 在关键操作、代码讲解、UI 交互等位置插入 `Screenshot-[mm:ss]` 占位符
- 调用 `ffmpeg` 自动截图
- 将占位符替换为本地图片链接，输出最终图文 Markdown

## 目录结构

- `SKILL.md`：skill 主说明
- `scripts/replace_screenshots.py`：把截图占位符替换为本地截图
- `references/screenshot-heuristics.md`：截图判断参考规则

## 依赖

- `ffmpeg`
- `python3`

## 使用方式

把这个目录安装到 Codex skills 后，在包含视频和 `.srt` 的工作目录中调用 `video-subtitle-markdown` 即可。
