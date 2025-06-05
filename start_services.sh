#!/bin/bash

echo "启动图书馆AI推荐监控服务..."
echo "当前API后端配置请查看 web_monitor.py 文件顶部"

# 启动主监控服务
python web_monitor.py
