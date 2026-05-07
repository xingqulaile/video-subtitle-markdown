# video-subtitle-markdown

一个给 Codex 使用的 skill：当用户提供视频文件和 `.srt` 字幕文件时，把内容整理成带本地截图的图文 Markdown 成品。

它适合屏幕录制、软件演示、网页操作、代码讲解、产品 walkthrough 这类内容。目标不是只把字幕抄成笔记，而是生成一篇真正可阅读、可复现的图文记录。

## 功能

- 读取 `.srt` 字幕并整理成 Markdown 笔记
- 在关键操作、代码讲解、UI 交互等位置插入 `Screenshot-[mm:ss]` 占位符
- 调用 `ffmpeg` 自动截图
- 将占位符替换为本地图片链接，输出最终图文 Markdown

## 适用场景

- 录了一段屏幕演示视频，想快速整理成图文教程
- 做了一个软件操作 walkthrough，想产出可分享的 Markdown 笔记
- 录了代码讲解视频，希望保留完整原话并补上关键截图
- 想把视频内容沉淀到知识库，而不是只保留一份 `.srt`

## 仓库结构

```text
video-subtitle-markdown/
├── SKILL.md
├── README.md
├── references/
│   └── screenshot-heuristics.md
├── scripts/
│   └── replace_screenshots.py
├── examples/
│   └── demo-note.md
└── docs/
    └── social-post.md
```

## 依赖

- `ffmpeg`
- `python3`
- 已安装并可用的 Codex

## 安装

### 1. 安装到 Codex skills 目录

如果你本地已经有这个仓库，可以把目录复制到 `~/.codex/skills/video-subtitle-markdown`。

如果你希望通过 GitHub 仓库安装，可以使用 Codex 的 skill 安装能力，从这个仓库拉取到本地 skills 目录。

### 2. 确认系统依赖

先确认这两个命令可用：

```bash
python3 --version
ffmpeg -version
```

如果 `ffmpeg` 不可用，截图替换阶段会失败，此时 Markdown 中会保留 `Screenshot-[mm:ss]` 占位符。

## 使用方法

### 输入文件

把这些文件放到同一个工作目录：

- 一个视频文件，例如 `demo.mov`
- 一个对应字幕文件，例如 `demo.srt`

优先使用同名文件组合，例如：

```text
demo.mov
demo.srt
```

### 调用 skill

在 Codex 中调用 `video-subtitle-markdown`，并让它基于当前目录中的视频和字幕生成图文 Markdown。

### 处理流程

skill 会按这个顺序工作：

1. 读取 `.srt`
2. 整理为 Markdown 初稿
3. 在关键句子末尾插入 `Screenshot-[mm:ss]`
4. 运行 `scripts/replace_screenshots.py`
5. 输出带本地图片链接的最终 Markdown

## 输出结果

通常会得到这些产物：

- 原始整理稿，例如 `demo.md`
- 带截图的成品，例如 `demo_with_screenshots.md`
- 截图资源目录，例如 `assets/`

图片链接使用相对路径，便于你把整篇 Markdown 连同 `assets/` 一起搬到 Obsidian、Typora、知识库或 Git 仓库中。

## 示例

可以先看这个演示文件，快速理解最终产物会长什么样：

- [examples/demo-note.md](examples/demo-note.md)

## 常见问题

### 1. 会不会删减字幕原文

不会。这个 skill 的要求是完整保留字幕文字，只允许补标点、断句、分段和少量标题。

### 2. 什么情况下会插截图

优先插在这些位置：

- UI 操作
- 代码讲解
- 终端输出
- 参数修改
- 页面地址或仓库地址出现时
- 不看画面就很难复现的步骤

### 3. 如果某个时间点截图失败怎么办

脚本会保留原始占位符，不会把整篇 Markdown 破坏掉。你可以稍后手动调整时间点再重新运行。

## 对外介绍

如果你想发朋友圈、发帖或作为仓库介绍文案，可以直接参考：

- [docs/social-post.md](docs/social-post.md)
