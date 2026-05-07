现在我来演示，如何把一段屏幕录制视频和对应字幕，快速整理成一篇可阅读的图文 Markdown。

## 打开工作目录
首先把视频文件和 `.srt` 字幕文件放到同一个目录里。![screenshot](../assets/example_open_folder.jpg)
如果它们是同名文件，脚本会优先把它们识别为一组输入。

## 生成 Markdown 初稿
接着调用 `video-subtitle-markdown`，它会先读取字幕内容，再按语义整理成自然段。![screenshot](../assets/example_markdown_draft.jpg)
这个阶段不会删减原字幕文字，只会补充标点、断句和简短标题。

## 插入截图并替换
当句子里出现关键操作、UI 指代、代码讲解或终端输出时，skill 会在句末插入 `Screenshot-[mm:ss]`。![screenshot](../assets/example_placeholder.jpg)
随后 `replace_screenshots.py` 会调用 `ffmpeg` 截图，并把这些占位符替换成本地图片链接。![screenshot](../assets/example_final_output.jpg)

## 最终效果
最后得到的是一篇图文并茂的 Markdown，而不是只有纯文本的字幕转写结果。
这份成品很适合继续发布到知识库、教程文档、博客草稿或团队 SOP 中。
