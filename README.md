# Kimi-K2.5 Chat Applications

基于 AiHubMix API 的 Kimi-K2.5 聊天应用集。

## 版本说明

| 版本 | 描述 |
|------|------|
| v0.1 | 单次对话版本，无循环 |
| v1.0 | 基础聊天版本，支持多轮对话 |
| v2.0 | 支持对话历史存储 |
| v3.0 | 支持对话历史存储（优化版） |
| v4.0 | 流式输出版本，带 Loading 动画 |
| v5.0 | 任务拆解助手，支持单步执行、工具调用、流式输出 |

## 演示视频

查看 `自动化演示.mp4` 了解 v5.0 版本的功能演示。

## 使用方法

1. 安装依赖：
```bash
pip install openai requests
```

2. 设置 API Key：
```bash
# Windows
set AIHUBMIX_API_KEY=你的API密钥

# Linux/Mac
export AIHUBMIX_API_KEY=你的API密钥
```

3. 运行：
```bash
# v5.0 任务拆解助手（推荐）
python hello_v5.0.py

# v4.0 流式输出版本
python hello_v4.0.py

# v2.0 历史存储版本
python hello_v2.0.py
```

## v5.0 特性

- **单步执行**：输出任务 → 本地执行 → 汇报结果 → 继续下一步
- **工具调用**：支持 write_to_file, read_file, web_fetch, execute_command, python_eval, web_search
- **流式输出**：实时显示模型回复
- **自动执行**：工具执行结果自动反馈给模型，继续下一步

## 参考资料

- [Kimi-K2.5 API 文档](https://aihubmix.com/model/kimi-k2.5)
- [月之暗面 AI 平台](https://platform.moonshot.cn)
