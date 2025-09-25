from wechatspider_fixed import WeChatSpider


def download_rencent_articles_to_json(spider:WeChatSpider,account_name, top_n=5, days_back=30, use_selenium=False,auto_save=True):
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
    try:
        articles = spider.crawl_recent_articles(
            days_back=days_back,
            max_articles=top_n,
            use_selenium=use_selenium,
            account_name=account_name,
            auto_save=auto_save
        )

        #if articles:
            #spider.save_to_json_single_File(account_name=account_name)
            # spider.save_to_excel(account_name=account_name)

        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()


def download_rencent_articles_to_md(spider:WeChatSpider,account_name, top_n=5, days_back=30, use_selenium=False,auto_save=True):
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
    try:
        articles = spider.crawl_recent_articles_to_md(
            days_back=days_back,
            max_articles=top_n,
            use_selenium=use_selenium,
            account_name=account_name,
            auto_save=auto_save
        )

        #if articles:
            #spider.save_to_json_single_File(account_name=account_name)
            # spider.save_to_excel(account_name=account_name)

        return articles
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return []
    finally:
        spider.close_driver()