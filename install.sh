#!/bin/bash

# 显示欢迎信息
echo "=== Website Monitor Bot 安装脚本 ==="
echo "这个脚本将帮助您安装和配置网站监控机器人。"
echo

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用root用户运行此脚本"
    echo "您可以使用 'sudo -i' 切换到root用户"
    exit 1
fi

# 安装系统依赖
echo "正在安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv firefox-esr firefox-geckodriver git curl wget

# 确保python3-venv已安装
apt install -y python3-venv

# 创建安装目录
echo "创建安装目录..."
mkdir -p /opt/website-monitor
cd /opt/website-monitor

# 下载所需文件
echo "下载程序文件..."
wget -O main.py https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/main.py
wget -O monitor.py https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/monitor.py
wget -O start.sh https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/start.sh
wget -O stop.sh https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/stop.sh
wget -O requirements.txt https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/requirements.txt
wget -O .env.example https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/master/.env.example

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
python3 -m pip install --upgrade pip

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 配置环境变量
echo "配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "请输入您的Telegram Bot Token:"
    read -r token
    echo "请输入您的Chat ID:"
    read -r chat_id
    echo "请输入要监控的关键词（用逗号分隔）:"
    read -r keywords
    echo "请输入要监控的网站URL:"
    read -r url
    
    # 更新配置文件
    sed -i "s/your_bot_token_here/$token/" .env
    sed -i "s/your_chat_id_here/$chat_id/" .env
    sed -i "s/keyword1,keyword2,keyword3/$keywords/" .env
    sed -i "s|https://example.com/|$url|" .env
fi

# 设置权限
echo "设置权限..."
chmod +x start.sh stop.sh

# 创建系统服务
echo "创建系统服务..."
cat > /etc/systemd/system/website-monitor.service << EOL
[Unit]
Description=Website Monitor Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/website-monitor
ExecStart=/opt/website-monitor/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 启动服务
echo "启动服务..."
systemctl daemon-reload
systemctl enable website-monitor
systemctl start website-monitor

echo
echo "=== 安装完成 ==="
echo "您可以使用以下命令管理服务："
echo "启动: systemctl start website-monitor"
echo "停止: systemctl stop website-monitor"
echo "重启: systemctl restart website-monitor"
echo "查看状态: systemctl status website-monitor"
echo "查看日志: journalctl -u website-monitor -f"
echo
echo "程序已安装在 /opt/website-monitor 目录"
echo "配置文件位置: /opt/website-monitor/.env" 