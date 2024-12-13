import os
import time
import asyncio
from dotenv import load_dotenv
from monitor import NodeseekMonitor

async def main():
    # 加载环境变量
    load_dotenv()
    
    # 初始化监控器
    monitor = NodeseekMonitor()
    
    try:
        await monitor.monitor_posts()
    except KeyboardInterrupt:
        print("程序被用户终止")
    except Exception as e:
        print(f"程序异常终止: {str(e)}")
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序被用户终止")
    except Exception as e:
        print(f"程序异常终止: {str(e)}") 