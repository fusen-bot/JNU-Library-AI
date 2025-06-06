# API 后端切换指南

## 概述
本系统支持三种AI API后端：
- **星火API (Spark)**: 讯飞星火认知大模型
- **千问API (Qwen)**: 阿里云千问大模型  
- **OpenAI API (OpenAI)**: OpenAI GPT模型

## 如何切换API后端

### 1. 修改配置
打开 `web_monitor.py` 文件，找到顶部的API配置区域：

```python
# ===========================================
# API 配置区域 - 在这里切换不同的后端API
# ===========================================
# 可选值: "spark" (星火API) 或 "qwen" (千问API) 或 "openai" (OpenAI API)
API_BACKEND = "spark"  # 修改这里来切换API
```

### 2. 修改配置值
- 使用星火API: `API_BACKEND = "spark"`
- 使用千问API: `API_BACKEND = "qwen"`
- 使用OpenAI API: `API_BACKEND = "openai"`

### 3. 重启服务
修改配置后，需要重启web监控服务才能生效：

```bash
# 停止当前服务 (Ctrl+C)
# 然后重新启动
python web_monitor.py
```

## API配置说明

### 星火API配置
在 `spark.py` 文件中配置：
```python
API_PASSWORD = "你的星火API密钥"
```

### 千问API配置
在 `qwen.py` 文件中配置：
```python
API_KEY = "你的千问API密钥"
```

### OpenAI API配置
在 `openai.py` 文件中配置：
```python
OPENAI_API_KEY = "你的OpenAI API密钥"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 可修改为其他兼容端点
```

**注意**: 对于OpenAI API，你可以：
- 使用官方OpenAI API
- 使用兼容OpenAI格式的第三方API（如Azure OpenAI、本地部署的模型等）
- 修改`OPENAI_BASE_URL`指向你的API端点

## 注意事项
1. 确保相应的API密钥已正确配置
2. 确保安装了所需依赖：`pip install -r requirements.txt`
3. 三个API的输出格式是统一的，切换后无需修改前端代码
4. 系统启动时会在日志中显示当前使用的API后端
5. OpenAI API需要有效的API密钥和网络连接

## 故障排除
- 如果切换后无法正常工作，请检查API密钥是否正确
- 查看终端日志输出，确认当前使用的API后端
- 确保网络连接正常，可以访问对应的API服务 