import os
import json
import logging
import asyncio
import atexit
from datetime import datetime
from pathlib import Path
from telegram import Bot
from dotenv import load_dotenv
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 创建log文件夹
log_dir = Path('log')
log_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 加载环境变量
load_dotenv()

class NodeseekMonitor:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        self.keywords = os.getenv('KEYWORDS').lower().split(',')
        self.check_interval = int(os.getenv('CHECK_INTERVAL'))
        self.target_url = os.getenv('TARGET_URL')
        self.bot = Bot(token=self.bot_token)
        self.seen_posts_file = 'seen_posts.json'
        self.seen_posts = self.load_seen_posts()
        
        # 设置Chrome选项
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无界面模式
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 初始化WebDriver
        self.driver = None
        
        # 注册退出处理函数
        atexit.register(self.cleanup)

    def cleanup(self):
        """清理资源"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            logging.error(f"清理资源时出错: {str(e)}")

    def get_random_user_agent(self):
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0',
        ]
        return random.choice(user_agents)

    def init_driver(self):
        """初始化或重新初始化WebDriver"""
        try:
            if self.driver:
                self.cleanup()
            
            # 每次初始化时随机化User-Agent
            self.chrome_options.add_argument(f'--user-agent={self.get_random_user_agent()}')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_options
            )
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            
            # 设置窗口大小为随机值
            width = random.randint(1024, 1920)
            height = random.randint(768, 1080)
            self.driver.set_window_size(width, height)
            
            logging.info("WebDriver初始化成功")
        except Exception as e:
            logging.error(f"初始化WebDriver失败: {str(e)}")
            raise

    def load_seen_posts(self):
        """加载已经发送过的帖子ID"""
        if Path(self.seen_posts_file).exists():
            try:
                with open(self.seen_posts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error(f"JSON文件损坏，创建新的记录")
                return []
        return []

    def save_seen_posts(self):
        """保存已发送的帖子ID"""
        try:
            with open(self.seen_posts_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存已发送帖子记录失败: {str(e)}")

    async def send_telegram_message(self, message):
        """发送Telegram消息"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logging.info(f"消息已发送: {message}")
        except Exception as e:
            logging.error(f"发送消息失败: {str(e)}")

    def check_keywords(self, text):
        """检查文本是否包含关键词"""
        text = text.lower()
        matched_keywords = [keyword for keyword in self.keywords if keyword in text]
        if matched_keywords:
            logging.info(f"匹配到关键词: {matched_keywords}")
            return True
        return False

    def save_html_content(self, html):
        """保存HTML内容到log文件夹"""
        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # file_path = log_dir / f'page_{timestamp}.txt'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"URL: {self.target_url}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n")
                f.write(html)
            logging.info(f"页面内容已保存到: {file_path}")
        except Exception as e:
            logging.error(f"保存页面内容失败: {str(e)}")

    async def fetch_posts(self):
        """获取网站帖子"""
        try:
            if not self.driver:
                logging.error("WebDriver未初始化")
                return []
            
            # 访问页面
            self.driver.get(self.target_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 随机等待一段时间
            await asyncio.sleep(random.uniform(1, 3))
            
            # 获取页面内容
            html = self.driver.page_source
            if not html:
                logging.error("获取页面内容失败")
                return []
                
            logging.info(f"成功获取页面，长度: {len(html)} 字符")
            
            # 保存页面内容到log文件夹
            self.save_html_content(html)
            
            # 解析页面
            soup = BeautifulSoup(html, 'html.parser')
            posts = []
            
            # 记录找到的HTML结构
            logging.info(f"页面标题: {soup.title.string if soup.title else 'No title found'}")
            
            # 1. 查找post-list-item
            post_items = soup.find_all('li', class_='post-list-item')
            logging.info(f"找到 {len(post_items)} 个post-list-item")
            
            # 处理每个post-list-item
            for post in post_items:
                try:
                    # 查找帖子标题链接
                    title_link = post.find('div', class_='post-title').find('a')
                    if not title_link:
                        continue
                        
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    if not title or not href:
                        continue
                    
                    # 构建完整链接
                    full_link = href if href.startswith('http') else f"{self.target_url.rstrip('/')}{href}"
                    
                    # 使用链接作为唯一标识
                    post_id = href
                    
                    posts.append({
                        'id': post_id,
                        'title': title,
                        'link': full_link
                    })
                    logging.info(f"成功解析帖子: {title} | URL: {full_link}")
                    
                except Exception as e:
                    logging.error(f"解析帖子时出错: {str(e)}")
                    continue
            
            # 2. 如果没有找到post-list-item，尝试其他可能的结构
            if not posts:
                # 查找所有可能的帖子链接
                all_links = soup.find_all('a')
                for link in all_links:
                    href = link.get('href', '')
                    if href and ('/post-' in href or '/t/' in href or '/topic/' in href):
                        title = link.get_text(strip=True)
                        if title:  # 如果链接有文本内容
                            full_link = href if href.startswith('http') else f"{self.target_url.rstrip('/')}{href}"
                            posts.append({
                                'id': href,
                                'title': title,
                                'link': full_link
                            })
                            logging.info(f"成功解析帖子(备用方法): {title} | URL: {full_link}")
            
            logging.info(f"总共找到 {len(posts)} 个帖子")
            return posts
            
        except Exception as e:
            logging.error(f"获取帖子失败: {str(e)}")
            return []

    async def monitor_posts(self):
        """监控帖子的主函数"""
        logging.info("开始监控...")
        logging.info(f"监控关键词: {self.keywords}")
        
        try:
            while True:
                try:
                    # 每次循环都重新初始化WebDriver
                    self.cleanup()
                    self.init_driver()
                    
                    posts = await self.fetch_posts()
                    for post in posts:
                        if post['id'] not in self.seen_posts and self.check_keywords(post['title']):
                            message = (
                                f"🔔 发现新帖子!\n\n"
                                f"📌 标题: {post['title']}\n"
                                f"🔗 链接: {post['link']}\n"
                                f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            await self.send_telegram_message(message)
                            self.seen_posts.append(post['id'])
                            self.save_seen_posts()

                    # 清理当前的WebDriver
                    self.cleanup()
                    
                    # 随机化检查间隔
                    actual_interval = self.check_interval + random.randint(-10, 10)
                    logging.info(f"检查完成，等待 {actual_interval} 秒后重新检查...")
                    await asyncio.sleep(actual_interval)
                except asyncio.CancelledError:
                    logging.info("监控任务被取消")
                    break
                except Exception as e:
                    logging.error(f"监控过程中出错: {str(e)}")
                    self.cleanup()  # 确保清理资源
                    await asyncio.sleep(60)  # 出错后等待1分钟再重试
        finally:
            self.cleanup()

async def main():
    monitor = NodeseekMonitor()
    try:
        await monitor.monitor_posts()
    except KeyboardInterrupt:
        logging.info("程序被用户终止")
    except Exception as e:
        logging.error(f"程序异常终止: {str(e)}")
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("程序被用户终止")
    except Exception as e:
        logging.error(f"程序异常终止: {str(e)}") 