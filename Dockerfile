# 使用官方Python 3.12 slim镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 重命名Docker专用的web_monitor文件
RUN cp web_monitor_docker.py web_monitor.py

# 创建一个非root用户来运行应用
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# 暴露Flask服务端口
EXPOSE 5001

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动虚拟显示器（用于Chrome headless模式）\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
# 等待虚拟显示器启动\n\
sleep 2\n\
# 启动应用\n\
python web_monitor.py' > /app/start.sh && chmod +x /app/start.sh

# 设置启动命令
CMD ["./start.sh"]