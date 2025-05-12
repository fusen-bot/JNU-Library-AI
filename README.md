# 江南大学图书馆检索系统输入词监听与智能AI提示关键词

这个项目实现本地监听网页输入行为并提供智能反馈提示关键词。

## 功能特点

- 监听网页中的所有输入字段，包括输入框和文本域（目标网页https://opac.jiangnan.edu.cn/#/Home）
- 捕获用户输入内容并发送到本地服务器
- 使用讯飞星火API生成智能输入建议（模调用教程：https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_1-%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E）
- 在网页上显示实时建议反馈

## 技术架构

- **Python**: 控制Selenium浏览器和处理请求
- **Selenium**: 自动化浏览器操作和JS注入
- **Flask**: 提供本地API服务
- **JavaScript**: 在网页前端捕获输入事件和显示建议

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

