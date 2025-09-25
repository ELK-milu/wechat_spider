from datetime import datetime

import requests
from bs4 import BeautifulSoup
import html2text
import re
import os
import io  # 用于在内存中创建文件对象

class WeChatArticleExtractor:
    def __init__(self):
        self.article_title = ""
        self.publish_time = ""
        self.content = ""


def check_url_valid(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=15)  # 增加超时时间
    response.raise_for_status()  # 检查 HTTP 请求是否成功
    if response.status_code == 200:
        return True
    else:
        return False

# 将之前的提取逻辑放入一个独立的函数
def extract_wechat_article_to_markdown(url,time,filtter_map=True):
    """
    从微信公众号文章 URL 提取 Markdown 内容，包括标题。
    尝试多种方法获取文章标题。

    Args:
        url (str): 微信公众号文章的 URL。
        time (str): 文章的发布时间，格式为 "YYYY-MM-DD"。
        filtter_map (bool): 是否过滤掉文章中的图片，默认为 True。
    Returns:
        str: 转换后的 Markdown 内容（包含标题），如果失败则返回 None。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        article = WeChatArticleExtractor()
        response = requests.get(url, headers=headers, timeout=15)  # 增加超时时间
        response.raise_for_status()  # 检查 HTTP 请求是否成功
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # --- 1. 提取文章主标题 ---
        article.article_title = ""
        # 方法 A: 尝试从 <meta property="og:title"> 获取 (最推荐，用于社交分享的标准化标题)
        og_title_tag = soup.find('meta', property='og:title')

        if og_title_tag and 'content' in og_title_tag.attrs:
            article.article_title = og_title_tag['content'].strip()

        if not article.article_title:  # 如果 'og:title' 没有找到，尝试其他方法
            # 方法 B: 尝试从 <h2 id="activity-name"> 获取 (微信公众号常见的标题位置)
            title_tag_h2 = soup.find('h2', id='activity-name')
            if title_tag_h2:
                article.article_title = title_tag_h2.get_text(strip=True)

        if not article.article_title:  # 如果以上都没找到，尝试从 <title> 标签获取
            # 方法 C: 从 <title> 标签获取 (备用，格式可能不统一)
            title_tag_page = soup.find('title')
            if title_tag_page:
                full_title = title_tag_page.get_text(strip=True)
                # 尝试切割，移除公众号名称部分 (通常是 "文章标题 - 公众号名称")
                if ' - ' in full_title:
                    article.article_title = full_title.split(' - ')[0].strip()
                else:
                    article.article_title = full_title


        # --- 2. 提取文章发布时间 ---
        if not article.publish_time:
            article.publish_time = time

        # --- 3. 提取文章内容 ---
        article_content_div = soup.find('div', id='js_content')
        if not article_content_div:
            print(f"DEBUG: URL {url} - 未找到文章内容区域（ID 为 'js_content' 的 div）。")
            return "错误：无法找到文章内容区域。可能是文章结构改变或已被删除。"

        # 处理图片 data-src 及清理冗余属性
        for img in article_content_div.find_all('img'):
            if not filtter_map:
                if 'data-src' in img.attrs:
                    img['src'] = img['data-src']
                for attr in ['data-type', 'data-w', 'data-ratio', 'style']:
                    if attr in img.attrs:
                        del img[attr]
            else:
                img.decompose()  # 彻底移除图片标签


        # 移除无关紧要的 script 和 style 标签
        for s in article_content_div(['script', 'style', 'noscript']):
            s.extract()

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        h.single_line_break = True
        h.pad_alt_text = True
        h.ignore_emphasis = False  # 保留粗体/斜体
        h.ul_item_mark = '  '  # 尝试将无序列表符号替换为两个空格
        h.list_indent = '    '  # 列表缩进
        h.ignore_tables = False  # 保留表格

        markdown_content = h.handle(str(article_content_div))

        # 清理多余的空行和空白
        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
        markdown_content = markdown_content.strip()

        # --- 3. 将标题和内容组合成最终的 Markdown ---
        final_markdown = ""
        if article.article_title:
            final_markdown += f"# {article.article_title}\n\n"
        if article.publish_time:
            # 确保 publish_time 是字符串类型
            final_markdown += f"发布时间: {str(article.publish_time)}\n\n"

        final_markdown += markdown_content

        return final_markdown

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: 网络请求错误: {e}")
        return f"网络请求错误: {e}. 请检查 URL 或网络连接。"
    except Exception as e:
        print(f"DEBUG: 发生错误: {e}")
        return f"处理错误: {e}"

def save_to_local(str):
    # 将字符串内容保存到本地文件
    output_path = "output.md"
    with io.open(output_path, 'w', encoding='utf-8') as file:
        file.write(str)


if __name__ == '__main__':
    result = extract_wechat_article_to_markdown("https://mp.weixin.qq.com/s?__biz=MzA3MzEwOTAxOQ==&mid=2652623171&idx=1&sn=f56cd86fc921f411a28020ada0a6fe01&chksm=84fb6a37b38ce3216133e9e7c048c2c3c86f091745527b24340df8e780a8f61ba02e06cb7034#rd","2025-12-1")
    save_to_local(result)