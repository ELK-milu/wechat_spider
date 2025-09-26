import traceback
import requests
import pandas as pd  # 引入 pandas 处理数据
from pprint import pprint

from utils.auto_login import WeChatLogin

# 创建 requests 会话
__session = requests.Session()
__headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}
__params = {
    "lang": "zh_CN",
    "f": "json",
}

def get_fakeid(nickname):
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
        "token": __params.get("token"),
    }

    try:
        response = __session.get(search_url, headers=__headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "list" in data and data["list"]:
            return data["list"][0].get('fakeid')
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except Exception as e:
        print(f"解析公众号 {nickname} 的 fakeid 失败: {traceback.format_exc()}")
        return None


def get_all_articles(nickname, fakeid, max_pages=20):
    """自动翻页获取公众号的所有文章"""
    if not fakeid:
        print(f"无效的 fakeid，无法获取 {nickname} 文章。")
        return []

    art_url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
    begin = 0  # 从第 0 条开始
    all_articles = []
    page = 1  # 记录当前爬取的页数

    while page <= max_pages:
        params = {
            "sub": 'list',
            "query": '',
            "begin": 0,
            "count": 5,  # 每页尝试获取最多20篇
            "type": "101_1",
            "free_publish_type" : "1",
            "search_field" : None,
            "sub_action": 'list_ex',
            "fakeid": fakeid,
            "lang": "zh_CN",
            "f": "json",
            "ajax":1,
            "token": __params.get("token"),
        }

        try:
            response = __session.get(art_url, headers=__headers, params=params)
            response.raise_for_status()
            msg_json = response.json()
            print(msg_json)

        except Exception as e:
            print(f"解析文章失败: {traceback.format_exc()}")
            break

    return all_articles


def save_to_excel(articles, filename="公众号文章.xlsx"):
    """保存文章数据为 Excel 文件"""
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False, engine="openpyxl")  # ✅ 移除 encoding
    print(f"✅ 文章数据已保存为 Excel 文件: {filename}")


def main():
    nickname = "聚光科技"
    loginer = WeChatLogin()
    infos = loginer.gzhlogin()
    __headers["Cookie"] = infos.get("cookie")
    __params["token"] = infos.get("token")

    fakeid = get_fakeid(nickname)
    if not fakeid:
        print(f"未能找到公众号 {nickname} 的 fakeid，请检查是否输入正确。")
        return

    print(f"获取到 {nickname} 的 fakeid: {fakeid}")

    articles = get_all_articles(nickname, fakeid)

    if articles:
        print(f"共获取到 {len(articles)} 篇文章")
        # 选择保存格式
        save_to_excel(articles, "公众号文章_1.xlsx")  # 保存 Excel


if __name__ == '__main__':
    main()

