#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号爬虫便捷函数库
基于用户修正代码，提供各种便捷的下载函数
"""

from wechatspider_fixed import WeChatSpider
import datetime

# ============== 单账号下载函数 ==============

def download_latest(account_name, use_selenium=False):
    """
    下载指定公众号的最新一篇文章
    
    Args:
        account_name (str): 公众号名称 ("粤政会计", "瑞幸咖啡", "威科先行")
        use_selenium (bool): 是否使用Selenium（默认False，使用requests更稳定）
    
    Returns:
        dict: 文章信息，失败返回None
    """
    print(f"🚀 开始下载【{account_name}】最新文章...")
    
    spider = WeChatSpider()
    try:
        article = spider.crawl_latest_article(
            use_selenium=use_selenium,
            account_name=account_name
        )
        return article
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None
    finally:
        spider.close_driver()

def download_recent_week(account_name, max_articles=10, use_selenium=False):
    """
    下载指定公众号最近一周的文章
    
    Args:
        account_name (str): 公众号名称
        max_articles (int): 最大文章数量
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 文章列表
    """
    print(f"🚀 开始下载【{account_name}】最近一周文章，最多{max_articles}篇...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_recent_articles(
            days_back=7,
            max_articles=max_articles,
            use_selenium=use_selenium,
            account_name=account_name
        )
        if articles:
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def download_recent_month(account_name, max_articles=50, use_selenium=False):
    """
    下载指定公众号最近一个月的文章
    
    Args:
        account_name (str): 公众号名称
        max_articles (int): 最大文章数量
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 文章列表
    """
    print(f"🚀 开始下载【{account_name}】最近一个月文章，最多{max_articles}篇...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_recent_articles(
            days_back=30,
            max_articles=max_articles,
            use_selenium=use_selenium,
            account_name=account_name
        )
        if articles:
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def download_recent_quarter(account_name, max_articles=100, use_selenium=False):
    """
    下载指定公众号最近三个月的文章
    
    Args:
        account_name (str): 公众号名称
        max_articles (int): 最大文章数量
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 文章列表
    """
    print(f"🚀 开始下载【{account_name}】最近三个月文章，最多{max_articles}篇...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_recent_articles(
            days_back=90,
            max_articles=max_articles,
            use_selenium=use_selenium,
            account_name=account_name
        )
        if articles:
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def download_custom_period(account_name, days_back, max_articles=50, use_selenium=False):
    """
    下载指定公众号自定义时间段的文章
    
    Args:
        account_name (str): 公众号名称
        days_back (int): 向前追溯天数
        max_articles (int): 最大文章数量
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 文章列表
    """
    print(f"🚀 开始下载【{account_name}】最近{days_back}天文章，最多{max_articles}篇...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_recent_articles(
            days_back=days_back,
            max_articles=max_articles,
            use_selenium=use_selenium,
            account_name=account_name
        )
        if articles:
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

# ============== 多账号下载函数 ==============

def download_all_latest(use_selenium=False):
    """
    下载所有公众号的最新文章
    
    Args:
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 所有文章列表
    """
    print("🚀 开始下载所有公众号最新文章...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_all_accounts_latest(use_selenium=use_selenium)
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def download_all_recent_week(max_articles_per_account=10, use_selenium=False):
    """
    下载所有公众号最近一周的文章
    
    Args:
        max_articles_per_account (int): 每个公众号最大文章数
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        dict: {公众号名称: [文章列表]}
    """
    print(f"🚀 开始下载所有公众号最近一周文章，每个账号最多{max_articles_per_account}篇...")
    
    spider = WeChatSpider()
    results = {}
    
    try:
        for account_name in spider.FAKEIDS.keys():
            print(f"\n📱 处理公众号: {account_name}")
            articles = spider.crawl_recent_articles(
                days_back=7,
                max_articles=max_articles_per_account,
                use_selenium=use_selenium,
                account_name=account_name
            )
            results[account_name] = articles
            
            if articles:
                spider.save_to_json(account_name=account_name)
                spider.save_to_excel(account_name=account_name)
            
            # 重置articles避免混淆
            spider.articles = []
        
        return results
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return {}
    finally:
        spider.close_driver()

def download_all_recent_month(max_articles_per_account=50, use_selenium=False):
    """
    下载所有公众号最近一个月的文章
    
    Args:
        max_articles_per_account (int): 每个公众号最大文章数
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        dict: {公众号名称: [文章列表]}
    """
    print(f"🚀 开始下载所有公众号最近一个月文章，每个账号最多{max_articles_per_account}篇...")
    
    spider = WeChatSpider()
    results = {}
    
    try:
        for account_name in spider.FAKEIDS.keys():
            print(f"\n📱 处理公众号: {account_name}")
            articles = spider.crawl_recent_articles(
                days_back=30,
                max_articles=max_articles_per_account,
                use_selenium=use_selenium,
                account_name=account_name
            )
            results[account_name] = articles
            
            if articles:
                spider.save_to_json(account_name=account_name)
                spider.save_to_excel(account_name=account_name)
            
            # 重置articles避免混淆
            spider.articles = []
        
        return results
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return {}
    finally:
        spider.close_driver()

# ============== 特殊功能函数 ==============

def download_by_keyword(account_name, keyword, days_back=30, max_articles=20, use_selenium=False):
    """
    下载包含特定关键词的文章（在标题中搜索）
    
    Args:
        account_name (str): 公众号名称
        keyword (str): 搜索关键词
        days_back (int): 向前追溯天数
        max_articles (int): 最大文章数量
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 匹配的文章列表
    """
    print(f"🚀 开始下载【{account_name}】包含关键词'{keyword}'的文章...")
    
    spider = WeChatSpider()
    try:
        # 先获取所有文章
        all_articles = spider.crawl_recent_articles(
            days_back=days_back,
            max_articles=max_articles,
            use_selenium=use_selenium,
            account_name=account_name
        )
        
        # 过滤包含关键词的文章
        matched_articles = []
        for article in all_articles:
            if keyword.lower() in article['title'].lower():
                matched_articles.append(article)
        
        print(f"🎯 在{len(all_articles)}篇文章中找到{len(matched_articles)}篇包含关键词'{keyword}'的文章")
        
        if matched_articles:
            # 保存过滤后的结果
            spider.articles = matched_articles
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        
        return matched_articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def download_top_articles(account_name, top_n=5, days_back=30, use_selenium=False):
    """
    下载指定公众号最近的前N篇文章（按发布时间排序）
    
    Args:
        account_name (str): 公众号名称
        top_n (int): 前N篇文章
        days_back (int): 向前追溯天数
        use_selenium (bool): 是否使用Selenium
    
    Returns:
        list: 前N篇文章列表
    """
    print(f"🚀 开始下载【{account_name}】最近{days_back}天的前{top_n}篇文章...")
    
    spider = WeChatSpider()
    try:
        articles = spider.crawl_recent_articles(
            days_back=days_back,
            max_articles=top_n,
            use_selenium=use_selenium,
            account_name=account_name
        )
        
        if articles:
            spider.save_to_json(account_name=account_name)
            spider.save_to_excel(account_name=account_name)
        
        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()

def get_article_summary(account_name, days_back=7):
    """
    获取指定公众号的文章数量统计（不下载内容，只统计）
    
    Args:
        account_name (str): 公众号名称
        days_back (int): 向前追溯天数
    
    Returns:
        dict: 统计信息
    """
    print(f"🚀 开始统计【{account_name}】最近{days_back}天的文章数量...")
    
    spider = WeChatSpider()
    try:
        # 获取文章链接（不获取详细内容）
        links = []
        page = 0
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        
        while True:
            page_links = spider.fetch_article_links(begin=page*5, count=5, account_name=account_name)
            
            if not page_links:
                break
            
            for link in page_links:
                pub_dt = datetime.datetime.strptime(link["pub_time"], "%Y-%m-%d %H:%M:%S")
                if pub_dt >= cutoff_date:
                    links.append(link)
                else:
                    break
            
            page += 1
            if page > 20:  # 防止无限循环
                break
        
        summary = {
            "account_name": account_name,
            "days_back": days_back,
            "total_articles": len(links),
            "latest_article": links[0]["title"] if links else "无文章",
            "latest_pub_time": links[0]["pub_time"] if links else "无发布时间",
            "articles": [{"title": l["title"], "pub_time": l["pub_time"]} for l in links]
        }
        
        print(f"📊 统计完成：最近{days_back}天共{len(links)}篇文章")
        return summary
        
    except Exception as e:
        print(f"❌ 统计失败: {e}")
        return {}
    finally:
        spider.close_driver()

# ============== 便捷别名函数 ==============

# 单账号便捷函数


# ============== 测试函数 ==============

def test_all_functions():
    """测试所有函数"""
    print("🧪 开始测试所有函数...")
    
    # 测试单账号函数
    print("\n" + "="*50)
    print("测试单账号函数")
    print("="*50)

    recentweek = download_recent_week("威科先行")
    if recentweek:
        print(f"✅ 近一周文章测试成功，共{len(recentweek)}篇")
    
    # # 测试下载最新文章
    # latest = download_latest("威科先行")
    # if latest:
    #     print(f"✅ 最新文章测试成功: {latest['title']}")
    #
    # # 测试多账号函数
    # print("\n" + "="*50)
    # print("测试多账号函数")
    # print("="*50)
    #
    # # 测试下载所有最新文章
    # all_latest = download_all_latest()
    # if all_latest:
    #     print(f"✅ 所有最新文章测试成功，共{len(all_latest)}篇")
    #
    # # 测试统计功能
    # print("\n" + "="*50)
    # print("测试统计功能")
    # print("="*50)
    #
    # summary = get_article_summary("威科先行", days_back=7)
    # if summary:
    #     print(f"✅ 统计测试成功: {summary['total_articles']}篇文章")
    #
    # print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    test_all_functions() 