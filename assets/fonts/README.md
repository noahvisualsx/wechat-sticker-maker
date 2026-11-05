# Font Assets & Licensing

本项目在后处理阶段渲染中文文字。为了避免版权风险：
- 不在仓库中直接捆绑未授权商用字体。
- 运行时支持自动探测系统已有的中文字体（如 macOS 的 `Hiragino Sans GB.ttc`, `STHeiti Medium.ttc`，Linux 的 `wqy-microhei`, `SourceHanSans` 等）。
- 生产环境可通过环境变量 `STICKER_FONT_PATH` 或 CLI 参数 `--font` 指定合法授权的字体文件（如思源黑体、阿里巴巴普惠体等免商用字体）。
