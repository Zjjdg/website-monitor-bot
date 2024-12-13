#!/bin/bash

if [ -f "program.pid" ]; then
    pid=$(cat program.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "正在停止程序 (PID: $pid)..."
        kill $pid
        rm program.pid
        echo "程序已停止"
    else
        echo "程序未在运行"
        rm program.pid
    fi
else
    echo "找不到程序PID文件"
fi 