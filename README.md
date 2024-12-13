# Website Monitor Bot

一个基于 Python 的网站监控机器人，可以监控指定网站的新帖子，当发现包含关键词的帖子时，通过 Telegram 发送通知。

## 一键部署

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Zjjdg/website-monitor-bot/main/install.sh)"
```

## 手动部署步骤

1. 克隆仓库：
```bash
git clone https://github.com/Zjjdg/website-monitor-bot.git
cd website-monitor-bot
```

2. 安装依赖：
```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv firefox-esr firefox-geckodriver

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

4. 运行程序：
```bash
chmod +x start.sh stop.sh
./start.sh
```

## 配置说明

在 `.env` 文件中配置以下参数：

```env
TELEGRAM_BOT_TOKEN=你的机器人Token
CHAT_ID=接收消息的聊天ID
KEYWORDS=关键词1,关键词2,关键词3
CHECK_INTERVAL=120
TARGET_URL=https://example.com/
```

## 常用命令

- 启动程序：`./start.sh`
- 停止程序：`./stop.sh`
- 查看日志：`tail -f monitor.log`
- 查看状态：`ps aux | grep python3`

## 文件说明

- `main.py`: 程序入口
- `monitor.py`: 监控核心逻辑
- `start.sh`: 启动脚本
- `stop.sh`: 停止脚本
- `.env`: 配置文件
- `requirements.txt`: Python 依赖列表

## 注意事项

1. 确保服务器有足够的内存（建议至少512MB）
2. 需要 Python 3.7 或更高版本
3. 程序会在后台运行，日志保存在 `monitor.log` 文件中
4. 已发送的帖子记录保存在 `seen_posts.json` 文件中 