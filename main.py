from utils.auto_login import WeChatLogin
from utils.difyknowledgebase import datebase_post_pipeline
from web_function_addition import download_rencent_articles_to_json, download_rencent_articles_to_md
from wechatspider_fixed import WeChatSpider


if __name__ == "__main__":
    loginer = WeChatLogin()
    infos = loginer.gzhlogin()
    spider = WeChatSpider()
    spider.FAKEIDS = {
        "聚光科技": "MzA3MzEwOTAxOQ==",
    }
    spider.chrome_driver_path = "C:\Program Files\Google\Chrome\Application\chromedriver\chromedriver.exe"
    spider.TOKEN = infos.get("token")
    spider.COOKIE = infos.get("cookie")
    download_rencent_articles_to_md(spider, "聚光科技", top_n=9999, days_back=9999, use_selenium=True,save_hook=datebase_post_pipeline)
