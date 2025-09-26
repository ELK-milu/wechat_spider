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

from article_2_md import extract_wechat_article_to_markdown, check_url_valid


class WeChatSpider:
    def __init__(self):
        # ===【配置项 - 基于用户修正后的代码】===
        self.FAKEIDS = {
            "聚光科技": "MzA3MzEwOTAxOQ==",
        }
        self.chrome_driver_path = r"D:\各种installer\chormDriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        # 使用用户修正后的配置
        self.TOKEN = "516943987"
        self.COOKIE = "pgv_pvid=8898906321; RK=ScNFh3Rq8V; ptcz=22590a12a8e18cc94980e9eb09c767ed7b6ccf56c9207baf45a206f07c77a450; pac_uid=0_ccQAAksry1Ftm; _qimei_uuid42=192130a1c22100a53345d4972209f34e387a197eaf; _qimei_fingerprint=041da21d25c5068368e56d1e1ad58716; _qimei_h38=8f95fb0e3345d4972209f34e0200000e719213; suid=user_0_ccQAAksry1Ftm; qq_domain_video_guid_verify=82e6441ef09fd035; _qimei_q32=06cf930e956c8a7ee7f1febc85e3dc8e; _qimei_q36=b46e45efc8afb74fcfa9f02130001fc19419; omgid=0_ccQAAksry1Ftm; yyb_muid=3A5F65E1CB6B64123F867075CA286545; _qpsvr_localtk=0.7918347375085358; ptui_loginuin=2636626273@qq.com; rewardsn=; wxtokenkey=777; ua_id=xHtW305mySbToIGDAAAAAC7dd7XVTFRXoaetlUE_nfM=; _clck=h9qu6k|1|fy2|0; wxuin=53933276328488; mm_lang=zh_CN; uuid=d3b84645ce92c0aaa9c1d7765b51d2de; rand_info=CAESIPjx85fQSe2l+XTkyaI/Ml9zaURJuYhBlBpJ3OJ6KyY/; slave_bizuin=3861526152; data_bizuin=3861526152; bizuin=3861526152; data_ticket=j01VKpjvcsaERu728fHlP7ktRYTABlGcnTOrS/GIN9lBclfN7+dQAZwuVnHpmA4Y; slave_sid=X1ZKY0JUY1g2UW01S285YWQwZjVoRnV6OWVYRklFX1JSalFGWXhBN1pNNjhLRDN0NGExV3JuR05WRzBOeWZFckFKMjRzeENXbF9mZUkyOEZJYzRjOWxCVG1ER01Oa0NkNF9WOG95Wl9Xc3FYcWt2MEdaQ1BLZE42OHUwY2ljRWcxdjNvV2RXZnNOcVFiOTk3; slave_user=gh_9645c6c4cd12; xid=d36806718995eba11241783870b95cf0; _clsk=ehna6n|1753941766992|7|1|mp.weixin.qq.com/weheat-agent/payload/record"

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

    def get_headers(self):
        user_agent = random.choice(self.USER_AGENT_LIST)
        headers = {
            "Cookie": self.COOKIE,
            "User-Agent": user_agent,
        }
        return headers

    def get_fakeid(self,nickname):
        """获取微信公众号的 fakeid"""
        search_url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"

        params = {
            "action": "search_biz",
            "query": nickname,
            "begin": 0,
            "count": 1,
            "ajax": "1",
            "lang": "zh_CN",
            "f": "json",
            "token": self.TOKEN,
        }

        try:
            response = requests.get(search_url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            data = response.json()

            if "list" in data and data["list"]:
                print(f"获取到 {nickname} 的 fakeid: {data['list'][0]['fakeid']}")
                return data["list"][0].get('fakeid')
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except Exception as e:
            print(f"解析公众号 {nickname} 的 fakeid 失败")
            return None


    def fetch_article_hyperlinks(self, begin=0, count=5, account_name=None):
        """获取文章链接列表 - 使用用户修正后的API和参数"""
        # 确定使用哪个公众号
        if account_name and account_name in self.FAKEIDS:
            target_fakeid = self.FAKEIDS[account_name]
            target_name = account_name
        else:
            target_name = list(self.FAKEIDS.keys())[0]
            target_fakeid = self.FAKEIDS[target_name]

        # 使用用户修正后的URL和参数结构
        url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"

        data = {
            "sub": 'list',
            "query": '',
            "begin": begin,
            "count": count,  # 每页尝试获取最多20篇
            "type": "101_1",
            "free_publish_type": "1",
            "search_field": None,
            "sub_action": 'list_ex',
            "fakeid": target_fakeid,
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
            "token": self.TOKEN,
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
            print(f"response: {content_json}")
            # 检查返回结果
            if "publish_page" not in content_json:
                print(f"返回数据异常: {content_json}")
                return []

            results = []
            # 解析外层JSON
            publish_page_str = content_json.get('publish_page', '{}')
            publish_page = json.loads(publish_page_str)

            # 获取文章列表
            publish_list = publish_page.get('publish_list', [])

            for item in publish_list:
                publish_info_str = item.get('publish_info', '{}')

                publish_info = json.loads(publish_info_str)

                # 获取文章详细信息
                appmsgex = publish_info.get('appmsgex', [])

                for article in appmsgex:
                    # 提取所需字段
                    title = article.get('title', '')
                    link = article.get('link', '')
                    author_name = article.get('author_name', '')

                    # 获取发布时间（优先使用publish_info中的create_time）
                    temp_time = publish_info.get('publish_info', {}).get('create_time', 0)
                    t = time.localtime(temp_time)
                    pub_time = time.strftime("%Y-%m-%d", t)
                    # 构建文章字典
                    article_dict = {
                        "title": title,
                        "url": link,
                        "pub_time": pub_time,
                        "account_name": author_name
                    }

                    results.append(article_dict)
            return results

        except Exception as e:
            print(f"❌ 获取文章链接失败: {e}")
            return []

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
            print(f"response: {content_json}")

            # 检查返回结果
            if "app_msg_list" not in content_json:
                print(f"返回数据异常: {content_json}")
                return []

            results = []
            for item in content_json["app_msg_list"]:
                print("item:", item)
                title = item.get("title", "")
                link = item.get("link", "")
                create_time = item.get("create_time", 0)

                # 转换时间格式
                t = time.localtime(create_time)
                pub_time = time.strftime("%Y-%m-%d", t)

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


            if os.path.exists(self.chrome_driver_path):
                print(f"使用本地ChromeDriver: {self.chrome_driver_path}")
                service = Service(executable_path=self.chrome_driver_path)
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

    def crawl_recent_articles(self, days_back=30, max_articles=10, use_selenium=False, account_name=None,auto_save=False):
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

                temp_time = article["pub_time"]
                temp_title = article["title"]
                temp_url = f"./data/{account_name}/{temp_time}/{temp_title}.json"
                print(f"🔗 处理文章: {temp_url})")
                if os.path.exists(temp_url):
                    print(f"⚠️ 文章 '{temp_title}' 已存在，跳过")
                    continue

                try:
                    # 检查文章日期
                    pub_dt = datetime.datetime.strptime(article["pub_time"], "%Y-%m-%d")
                    if pub_dt < cutoff_date:
                        print(f"⏰ 文章 '{article['title']}' 超出时间范围，跳过")
                        break

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

                        if auto_save:
                            # 保存单个文章到JSON文件
                            self.save_article_to_json(account_name=target_account,article=detail)

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


    def crawl_recent_articles_to_md(self, days_back=30, max_articles=10,save_hook:callable=None, use_selenium=False, account_name=None,auto_save=False,auto_stop=False):
        """爬取最近一段时间的文章"""
        target_account = account_name or list(self.FAKEIDS.keys())[0]
        print(f"🚀 开始爬取 {target_account} 最近{days_back}天的文章，最多{max_articles}篇...")

        all_articles = []
        now = datetime.datetime.now()
        cutoff_date = now - datetime.timedelta(days=days_back)

        page = 0
        total_fetched = 0
        failed_times = 0

        while total_fetched < max_articles:

            if auto_stop:
                if failed_times >= 3:
                    print("❌ 已无最新文章可爬取")
                    break

            print(f"📋 正在获取第{page+1}页文章链接...")
            links = self.fetch_article_hyperlinks(begin=page*5, count=5, account_name=target_account)

            if not links:
                print("📄 没有更多文章了")
                break

            for article in links:
                if total_fetched >= max_articles:
                    break

                temp_time = article["pub_time"]
                temp_title = article["title"]
                temp_url = f"./data/{account_name}/{temp_time}/{temp_title}.md"
                print(f"🔗 处理文章: {temp_url})")
                if os.path.exists(temp_url):
                    print(f"⚠️ 文章 '{temp_title}' 已存在，跳过")
                    failed_times += 1
                    continue

                try:
                    # 检查文章日期
                    pub_dt = datetime.datetime.strptime(article["pub_time"], "%Y-%m-%d")
                    date_str = pub_dt.strftime("%Y-%m-%d")
                    if pub_dt < cutoff_date:
                        print(f"⏰ 文章 '{article['title']}' 超出时间范围，跳过")
                        break

                    if check_url_valid(article["url"]):
                        detail = extract_wechat_article_to_markdown(article["url"], date_str)
                        all_articles.append(detail)
                        total_fetched += 1
                        print(f"✅ 已完成 {total_fetched}/{max_articles}")

                        if auto_save:
                            # 保存单个文章到JSON文件
                            save_path = self.save_article_to_md(account_name=target_account,time = date_str,title=temp_title,article=detail)
                        if save_hook and save_path is not None:
                            save_hook(title = temp_title+".md",content = detail)

                        # 添加延迟避免被封
                        time.sleep(random.randint(15, 25))
                    else:
                        print(f"❌ 文章内容获取失败: {article['title']}")

                except Exception as e:
                    print(f"❌ 处理文章时出错: {e}")
                    failed_times += 1
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

    def save_article_to_json(self, account_name, article):
        """保存article数据到JSON文件"""
        if not article:
            print("⚠️ 没有数据可保存")
            return

        folder = f"./data/{account_name}/"
        os.makedirs(os.path.dirname(folder), exist_ok=True)
        pubtime = article.get("pub_time")
        save_floder = folder + pubtime + "/"
        os.makedirs(os.path.dirname(save_floder), exist_ok=True)
        filename = save_floder + article.get('title',
                                             'NoneName' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + ".json"
        if os.path.exists(filename):
            print(f"⚠️ 文件已存在: {filename}，跳过保存")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            print(f"💾 JSON数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")
            return None

    def save_article_to_md(self, account_name, time, title, article):
        """保存article数据到md文件"""
        if not article:
            print("⚠️ 没有数据可保存")
            return None

        # 清理文件名中的非法字符
        def clean_filename(filename):
            # 定义Windows/Linux/Unix系统中不允许的文件名字符
            illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '!']
            for char in illegal_chars:
                filename = filename.replace(char, '_')
            # 同时去除首尾空格和点号
            filename = filename.strip().strip('.')
            # 限制文件名长度，避免路径过长
            if len(filename) > 100:
                filename = filename[:100]
            return filename

        folder = f"./data/{account_name}/"
        os.makedirs(os.path.dirname(folder), exist_ok=True)

        pubtime = time
        save_folder = folder + str(pubtime) + "/"
        os.makedirs(os.path.dirname(save_folder), exist_ok=True)

        # 清理标题作为文件名
        clean_title = clean_filename(title)
        filename = save_folder + clean_title + ".md"

        if os.path.exists(filename):
            print(f"⚠️ 文件已存在: {filename}，跳过保存")
            return filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article)
            print(f"💾 md数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存md文件失败: {e}")
            return None



    def save_to_json_single_File(self, account_name=None):
        """保存数据到JSON文件"""
        if not self.articles:
            print("⚠️ 没有数据可保存")
            return

        folder = f"./data/{account_name}/"
        os.makedirs(os.path.dirname(folder), exist_ok=True)
        for article in self.articles:
            pubtime = article.get("pub_time")
            save_floder = folder + pubtime + "/"
            os.makedirs(os.path.dirname(save_floder), exist_ok=True)
            filename = save_floder + article.get('title', 'NoneName'+ datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + ".json"
            if os.path.exists(filename):
                print(f"⚠️ 文件已存在: {filename}，跳过保存")
                continue
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)
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
                    #'内容摘要': article['content'][:200] + '...' if len(article['content']) > 200 else article['content'],
                    '内容摘要': article['content'],
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
        '''
        print("\n" + "="*50)
        print("测试: 爬取威科先行最新文章")
        print("="*50)
        
        latest = spider.crawl_latest_article(use_selenium=False, account_name="威科先行")
        if latest:
            print(f"✅ 测试成功！")
            print(f"📖 标题: {latest['title']}")
            print(f"📝 字数: {latest['word_count']}")
        '''

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