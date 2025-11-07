#!/bin/bash
# 停止图书馆AI推荐监控服务
# 端口配置: 5001 (与 web_monitor.py 中的端口保持一致)

PORT=5001

echo "正在停止图书馆AI推荐监控服务..."
echo "端口: $PORT"

# 查找并停止运行在指定端口的进程
PID=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
    echo "❌ 未找到运行在端口 $PORT 上的进程"
    echo "服务可能已经停止"
else
    echo "找到进程 PID: $PID"
    kill -9 $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 已成功停止服务 (PID: $PID)"
    else
        echo "❌ 停止服务失败"
    fi
fi

# 额外清理：停止可能残留的 Chrome/Selenium 进程
echo ""
echo "正在清理残留的 Chrome/Selenium 进程..."

# 查找并停止 Chrome 驱动进程
CHROME_PIDS=$(ps aux | grep -i "chrome.*selenium\|chromedriver" | grep -v grep | awk '{print $2}')

if [ -z "$CHROME_PIDS" ]; then
    echo "✅ 未发现残留的 Chrome/Selenium 进程"
else
    echo "发现残留进程: $CHROME_PIDS"
    for pid in $CHROME_PIDS; do
        kill -9 $pid 2>/dev/null
        echo "  已停止进程: $pid"
    done
    echo "✅ Chrome/Selenium 进程清理完成"
fi

echo ""
echo "服务停止完成！"

