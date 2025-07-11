#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号爬虫 - 基于用户修正后的link_spider重新合并
完全保持用户原始代码的逻辑和配置
"""

import os
import requests
import datetime
import json
import time
import math
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class WeChatSpider:
    def __init__(self):
        # ===【配置项 - 基于用户修正后的代码】===
        self.FAKEIDS = {
            "粤政会计": "MzAxNTM0NzU1Ng==",
            "瑞幸咖啡": "MzUxNDQ2OTc2MQ==",
            "威科先行": "MzA5MDAyODcwMQ=="
        }
        
        # 使用用户修正后的配置
        self.TOKEN = "1501983514"
        self.COOKIE = "appmsglist_action_3191926402=card; pgv_pvid=5423298048; ptcz=45db8b0b704ee1d4452bb9fcb496a4d45efe0c6707cf9f468597a4b744e8c778; o2_uin=1072864748; RK=1CfFfUVXZZ; _qimei_q36=; _qimei_h38=19c544adf6ddaab6cd866d6a0200000761861c; eas_sid=F1X7y4Q8Z7l1f0C9L550Q428o1; ua_id=sRdOzkZCOt8LUohMAAAAAA0bTaYSoAcTca2v74L7v8c=; wxuin=52040870730641; mm_lang=zh_CN; xid=5b5f9f5a00b9341beab9bae9cbee9d04; data_bizuin=3191926402; bizuin=3191926402; data_ticket=WeMKPP765jjz6S8qGYRHtOeCIn+jg8+FmboeG228aP1OHxiJj3sWFD6lAk0VC7+i; rand_info=CAESIBOyMZzjNR36/+TFGg17gF2NHS/nKeQsuXJ/86AL1322; slave_bizuin=3191926402; slave_user=gh_8297f1f670b7; slave_sid=ZXhqTFpTOHRpSFVZY2ZTSUpoMzFvZ3N3VnV3cUN3aGt4MGg2ZTR4V25GX19JVVVpeTdiOVFianJSS1RxRWNpUmdJS1lOMnM4Q3BoYXpaR1FmWlFZd2I0alhheXpVR2ZoQjByNDBfczIyRDNUOWlsbWdvVzlBRXZ6UTNWMWc1SWxnaUdQaHRJbzA1bk9pTUNn; _clck=3191926402|1|fxh|0; _clsk=ztwm2m|1752111910751|7|1|mp.weixin.qq.com/weheat-agent/payload/record"
        
        # 用户的User-Agent列表
        self.USER_AGENT_LIST = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36",
        ]
        
        # 创建数据文件夹结构
        os.makedirs("./data", exist_ok=True)
        for account_name in self.FAKEIDS.keys():
            os.makedirs(f"./data/{account_name}", exist_ok=True)
        os.makedirs("./data/mixed", exist_ok=True)
        
        # 存储文章数据
        self.articles = []
        self.driver = None
    
    def fetch_article_links(self, begin=0, count=5, account_name=None):
        """获取文章链接列表 - 使用用户修正后的API和参数"""
        # 确定使用哪个公众号
        if account_name and account_name in self.FAKEIDS:
            target_fakeid = self.FAKEIDS[account_name]
            target_name = account_name
        else:
            target_name = list(self.FAKEIDS.keys())[0]
            target_fakeid = self.FAKEIDS[target_name]
        
        # 使用用户修正后的URL和参数结构
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        
        data = {
            "token": self.TOKEN,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": str(begin),
            "count": str(count),
            "query": "",
            "fakeid": target_fakeid,
            "type": "9",
        }
        
        # 随机选择User-Agent
        user_agent = random.choice(self.USER_AGENT_LIST)
        headers = {
            "Cookie": self.COOKIE,
            "User-Agent": user_agent,
        }
        
        try:
            print(f"📡 请求文章链接: {target_name}")
            response = requests.get(url, headers=headers, params=data)
            
            if response.status_code != 200:
                print(f"请求失败: {response.status_code}")
                return []
            
            content_json = response.json()
            
            # 检查返回结果
            if "app_msg_list" not in content_json:
                print(f"返回数据异常: {content_json}")
                return []
            
            results = []
            for item in content_json["app_msg_list"]:
                title = item.get("title", "")
                link = item.get("link", "")
                create_time = item.get("create_time", 0)
                
                # 转换时间格式
                t = time.localtime(create_time)
                pub_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
                
                results.append({
                    "title": title,
                    "url": link,
                    "pub_time": pub_time,
                    "account_name": target_name
                })
                
            print(f"✅ 获取到 {len(results)} 篇文章链接")
            return results
            
        except Exception as e:
            print(f"❌ 获取文章链接失败: {e}")
            return []
    
    def fetch_article_content_requests(self, article):
        """使用requests获取文章内容"""
        try:
            print(f"📄 抓取内容: {article['title']}")
            
            # 使用随机User-Agent
            user_agent = random.choice(self.USER_AGENT_LIST)
            headers = {"User-Agent": user_agent}
            
            res = requests.get(article["url"], headers=headers, timeout=15)
            
            if res.status_code != 200:
                print(f"⚠️ 内容请求失败: {res.status_code}")
                return None
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 获取文章内容
            content_elem = soup.select_one("div.rich_media_content")
            if not content_elem:
                content_elem = soup.select_one("#js_content")
            content = content_elem.get_text(separator="\n", strip=True) if content_elem else ""
            
            # 获取文章标题
            title_elem = soup.select_one("h1.rich_media_title")
            title = title_elem.get_text(strip=True) if title_elem else article["title"]
            
            # 获取作者信息
            author_elem = soup.select_one("span.rich_media_meta_text")
            author = author_elem.get_text(strip=True) if author_elem else article.get("account_name", "未知公众号")
            
            # 获取图片链接
            images = []
            if content_elem:
                img_elements = content_elem.find_all('img')
                for img in img_elements:
                    src = img.get('data-src') or img.get('src')
                    if src and src.startswith('http'):
                        images.append(src)
            
            return {
                "title": title,
                "author": author,
                "account_name": article.get("account_name", "未知公众号"),
                "pub_time": article["pub_time"],
                "url": article["url"],
                "content": content,
                "images": images,
                "word_count": len(content),
                "crawl_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ 获取内容失败: {e}")
            return None
    
    def setup_selenium_driver(self):
        """设置Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--lang=zh-CN")
            
            # 尝试使用具体的ChromeDriver路径
            chrome_driver_path = r"D:\各种installer\chormDriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"
            
            if os.path.exists(chrome_driver_path):
                print(f"使用本地ChromeDriver: {chrome_driver_path}")
                service = Service(executable_path=chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print("本地ChromeDriver不存在，尝试自动下载...")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Selenium WebDriver 初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ Selenium WebDriver 初始化失败: {e}")
            return False
    
    def fetch_article_content_selenium(self, article):
        """使用Selenium获取文章内容"""
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return None
            
            self.driver.get(article["url"])
            time.sleep(2)  # 防止加载不完全
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            div = soup.find("div", class_="rich_media_content")
            content = div.get_text(separator="\n", strip=True) if div else ""
            
            # 获取标题
            title_elem = soup.select_one("h1.rich_media_title")
            title = title_elem.get_text(strip=True) if title_elem else article["title"]
            
            # 获取作者
            author_elem = soup.select_one("span.rich_media_meta_text")
            author = author_elem.get_text(strip=True) if author_elem else article.get("account_name", "未知公众号")
            
            # 获取图片
            images = []
            if div:
                img_elements = div.find_all('img')
                for img in img_elements:
                    src = img.get('data-src') or img.get('src')
                    if src and src.startswith('http'):
                        images.append(src)
            
            return {
                "title": title,
                "author": author,
                "account_name": article.get("account_name", "未知公众号"),
                "pub_time": article["pub_time"],
                "url": article["url"],
                "content": content,
                "images": images,
                "word_count": len(content),
                "crawl_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Selenium获取内容失败: {e}")
            return None
    
    def crawl_latest_article(self, use_selenium=False, account_name=None):
        """爬取最新的一篇文章"""
        target_account = account_name or list(self.FAKEIDS.keys())[0]
        print(f"🚀 开始爬取 {target_account} 最新文章...")
        
        # 获取文章链接
        links = self.fetch_article_links(begin=0, count=1, account_name=target_account)
        
        if not links:
            print("❌ 未获取到文章链接")
            return None
        
        latest_article = links[0]
        print(f"📖 找到最新文章: {latest_article['title']}")
        
        # 添加随机延迟避免被封
        time.sleep(random.randint(2, 5))
        
        # 获取文章详细内容
        if use_selenium:
            detail = self.fetch_article_content_selenium(latest_article)
            if detail is None:
                print("⚠️ Selenium方法失败，尝试requests方法...")
                detail = self.fetch_article_content_requests(latest_article)
        else:
            detail = self.fetch_article_content_requests(latest_article)
        
        if detail:
            self.articles = [detail]
            print(f"✅ 成功爬取文章: {detail['title']}")
            print(f"📱 公众号: {detail['account_name']}")
            print(f"📝 文章字数: {detail['word_count']} 字")
            
            # 保存文件
            self.save_to_json(account_name=target_account)
            self.save_to_excel(account_name=target_account)
            
            return detail
        else:
            print("❌ 文章内容获取失败")
            return None
    
    def crawl_recent_articles(self, days_back=30, max_articles=10, use_selenium=False, account_name=None):
        """爬取最近一段时间的文章"""
        target_account = account_name or list(self.FAKEIDS.keys())[0]
        print(f"🚀 开始爬取 {target_account} 最近{days_back}天的文章，最多{max_articles}篇...")
        
        all_articles = []
        now = datetime.datetime.now()
        cutoff_date = now - datetime.timedelta(days=days_back)
        
        page = 0
        total_fetched = 0
        
        while total_fetched < max_articles:
            print(f"📋 正在获取第{page+1}页文章链接...")
            links = self.fetch_article_links(begin=page*5, count=5, account_name=target_account)
            
            if not links:
                print("📄 没有更多文章了")
                break
            
            for article in links:
                if total_fetched >= max_articles:
                    break
                
                try:
                    # 检查文章日期
                    pub_dt = datetime.datetime.strptime(article["pub_time"], "%Y-%m-%d %H:%M:%S")
                    if pub_dt < cutoff_date:
                        print(f"⏰ 文章 '{article['title']}' 超出时间范围，跳过")
                        continue
                    
                    # 获取文章详细内容
                    if use_selenium:
                        detail = self.fetch_article_content_selenium(article)
                        if detail is None:
                            detail = self.fetch_article_content_requests(article)
                    else:
                        detail = self.fetch_article_content_requests(article)
                    
                    if detail:
                        all_articles.append(detail)
                        total_fetched += 1
                        print(f"✅ 已完成 {total_fetched}/{max_articles}")
                        
                        # 添加延迟避免被封
                        time.sleep(random.randint(15, 25))
                    else:
                        print(f"❌ 文章内容获取失败: {article['title']}")
                        
                except Exception as e:
                    print(f"❌ 处理文章时出错: {e}")
                    continue
            
            page += 1
            time.sleep(random.randint(2, 5))  # 页面间延迟
        
        self.articles = all_articles
        print(f"🎉 共成功爬取 {len(all_articles)} 篇文章")
        return all_articles
    
    def crawl_all_accounts_latest(self, use_selenium=False):
        """遍历所有公众号，爬取每个公众号的最新文章"""
        print(f"🚀 开始遍历所有公众号爬取最新文章...")
        print(f"📋 将爬取的公众号: {list(self.FAKEIDS.keys())}")
        
        all_articles = []
        
        for account_name in self.FAKEIDS.keys():
            print(f"\n{'='*50}")
            print(f"📱 正在处理公众号: {account_name}")
            
            try:
                latest = self.crawl_latest_article(use_selenium=use_selenium, account_name=account_name)
                if latest:
                    all_articles.append(latest)
                    print(f"✅ {account_name} 最新文章获取成功")
                else:
                    print(f"❌ {account_name} 最新文章获取失败")
                
                # 添加延迟避免被封（使用用户原始代码中的延迟策略）
                print("⏳ 等待后处理下一个公众号...")
                time.sleep(random.randint(15, 25))
                
            except Exception as e:
                print(f"❌ 处理公众号 {account_name} 时出错: {e}")
                continue
        
        # 保存混合数据
        if all_articles:
            self.articles = all_articles
            print(f"\n🎉 遍历完成！共成功爬取 {len(all_articles)} 个公众号的最新文章")
            self.save_to_json()  # 保存到mixed文件夹
            self.save_to_excel()
        
        return all_articles
    
    def generate_filename(self, base_name, extension, account_name=None):
        """生成带时间戳的文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if account_name and account_name in self.FAKEIDS:
            folder = f"./data/{account_name}"
            filename = f"{base_name}_{timestamp}.{extension}"
        else:
            folder = "./data/mixed"
            filename = f"{base_name}_{timestamp}.{extension}"
        
        return os.path.join(folder, filename)
    
    def save_to_json(self, account_name=None):
        """保存数据到JSON文件"""
        if not self.articles:
            print("⚠️ 没有数据可保存")
            return
        
        base_name = "latest_article" if len(self.articles) == 1 else "recent_articles"
        filename = self.generate_filename(base_name, "json", account_name)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
            print(f"💾 JSON数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")
            return None
    
    def save_to_excel(self, account_name=None):
        """保存数据到Excel文件"""
        if not self.articles:
            print("⚠️ 没有数据可保存")
            return
        
        base_name = "latest_article" if len(self.articles) == 1 else "recent_articles"
        filename = self.generate_filename(base_name, "xlsx", account_name)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            df_data = []
            for article in self.articles:
                df_data.append({
                    '公众号': article.get('account_name', '未知公众号'),
                    '标题': article['title'],
                    '作者': article['author'],
                    '发布时间': article['pub_time'],
                    '文章链接': article['url'],
                    '字数': article['word_count'],
                    '图片数量': len(article['images']),
                    '内容摘要': article['content'][:200] + '...' if len(article['content']) > 200 else article['content'],
                    '爬取时间': article['crawl_time']
                })
            
            df = pd.DataFrame(df_data)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"📊 Excel数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存Excel文件失败: {e}")
            return None
    
    def save_to_csv(self, account_name=None):
        """保存数据到CSV文件（兼容用户原始代码的保存格式）"""
        if not self.articles:
            print("⚠️ 没有数据可保存")
            return
        
        base_name = "articles_list"
        filename = self.generate_filename(base_name, "csv", account_name)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            df_data = []
            for article in self.articles:
                df_data.append({
                    'title': article['title'],
                    'link': article['url'],
                    'create_time': article['pub_time']
                })
            
            df = pd.DataFrame(df_data)
            df.to_csv(filename, mode='a', encoding='utf-8', index=False)
            print(f"📄 CSV数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存CSV文件失败: {e}")
            return None
    
    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 浏览器已关闭")
            except:
                pass

def main():
    """测试主函数"""
    spider = WeChatSpider()
    
    try:
        print("🎯 基于用户修正代码的微信公众号爬虫")
        print(f"📋 支持的公众号: {list(spider.FAKEIDS.keys())}")
        
        # 测试单个公众号
        print("\n" + "="*50)
        print("测试: 爬取威科先行最新文章")
        print("="*50)
        
        latest = spider.crawl_latest_article(use_selenium=False, account_name="威科先行")
        if latest:
            print(f"✅ 测试成功！")
            print(f"📖 标题: {latest['title']}")
            print(f"📝 字数: {latest['word_count']}")
        
        # 测试所有公众号
        spider.articles = []  # 清空数据
        
        print("\n" + "="*50)
        print("测试: 爬取所有公众号最新文章")
        print("="*50)
        
        all_latest = spider.crawl_all_accounts_latest(use_selenium=False)
        if all_latest:
            print(f"✅ 所有公众号测试成功，共获取 {len(all_latest)} 篇文章")
            for article in all_latest:
                print(f"📱 {article['account_name']}: {article['title']} ({article['word_count']} 字)")
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        spider.close_driver()

if __name__ == "__main__":
    main() 