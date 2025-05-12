#!/bin/bash

# 启动 Flask 服务
echo "启动 Flask 服务..."
python spark.py &  # 在后台运行

# 等待一段时间以确保 Flask 服务启动
sleep 2

# 启动监控服务
echo "启动监控服务..."
python web_monitor.py

# 等待用户输入以保持终端打开
wait
