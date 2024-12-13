#!/bin/bash

# 激活Python虚拟环境(如果存在)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 检查程序是否已在运行
if [ -f "program.pid" ]; then
    pid=$(cat program.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "程序已经在运行中 (PID: $pid)"
        exit 1
    else
        rm program.pid
    fi
fi

# 启动程序
echo "正在启动监控程序..."
nohup python3 main.py > monitor.log 2>&1 &

# 保存进程ID
echo $! > program.pid
echo "程序已启动 (PID: $!)"
echo "日志文件: monitor.log" 