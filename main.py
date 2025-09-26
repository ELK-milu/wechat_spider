from utils.auto_login import WeChatLogin
from utils.dify_knowledgebase import DifyKnowledgeBase
from web_function_addition import download_rencent_articles_to_json, download_rencent_articles_to_md
from wechatspider_fixed import WeChatSpider


if __name__ == "__main__":
    # 目前暂时只支持单个公众号爬取
    pulisher_name = "聚光科技"

    loginer = WeChatLogin()
    spider = WeChatSpider()
    dify_knowledge = DifyKnowledgeBase()

    infos = loginer.gzhlogin()

    spider.chrome_driver_path = "C:\Program Files\Google\Chrome\Application\chromedriver\chromedriver.exe"
    spider.TOKEN = infos.get("token")
    spider.COOKIE = infos.get("cookie")

    spider.FAKEIDS = {
        pulisher_name: spider.get_fakeid(pulisher_name),
    }

    download_rencent_articles_to_md(spider, pulisher_name, top_n=9999, days_back=9999, use_selenium=True,save_hook=dify_knowledge.datebase_post_pipeline,auto_stop=False)
