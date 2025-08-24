# 江南大学图书馆检索系统输入词监听与智能AI提示关键词（实验程序代码项目）

## 📁 文件结构

```
.
├── web_monitor.py             # 主服务，Selenium控制和API服务器
├── spark.py                   # 星火LLM集成
├── qwen.py                    # 千问LLM集成
├── openai.py                  # OpenAI LLM集成
├── show_books_with_reasons.js # 新版UI组件（用于测试页面）
├── suggestion_display.js      # 旧版UI组件（用于测试页面）
├── requirements.txt           # Python依赖
├── start_services.sh          # 启动脚本
├── README.md                  # 本文档
└── tests/
这个项目实现本地监听网页输入行为并提供智能反馈提示关键词。

## 功能特点

- 监听网页中的所有输入字段，包括输入框和文本域（目标网页https://opac.jiangnan.edu.cn/#/Home）
- 捕获用户输入内容并发送到本地服务器
- 使用大语言模型API生成智能输入建议（待更新：可以升级为三本书发送三次请求以便快速响应，加入实时更新字段在前端并返回，当有字段的时候就加载完成）
- 在网页上显示实时建议反馈

## 技术架构

- **后端**: `Python` + `Flask`
  - 作为API服务器，接收前端请求，并行调用LLM并返回结构化数据。【带优化转为流式输出返回字符】
- **核心驱动**: `Selenium`
  - 用于自动化浏览器操作，将前端监控脚本动态注入到目标网页。
- **前端注入**: `JavaScript`
  - 注入到目标网页的脚本，负责监听用户输入、调用后端API、并将返回的数据渲染成推荐理由UI。
- **LLM集成**: `spark.py`, `qwen.py`, `openai.py`
  - 模块化设计，每个文件负责与一个特定的大模型API进行交互。

## 安装步骤

1. 安装Python依赖：

```bash
pip install -r requirements.txt
```

2. 确保安装了Chrome浏览器（Selenium需要）

## 使用方法

1. 启动本地监控服务：

```bash
python spark.py
python web_monitor.py
```

2. 服务将自动启动Chrome浏览器并打开配置的网页(默认为http://localhost:3000)

3. 当你在网页中输入内容时，系统会自动分析输入并提供建议


