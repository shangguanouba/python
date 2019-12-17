import os
import time
import json
import random

import jieba
import requests
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# 词云图片
WC_MASK_IMG = "wawa.jpg"
# 评论数据保存文件
COMMENT_FILE_PATH = "jd_comment.txt"
# 词云字体
WC_FONT_PATH = "STLITI.TTF"


def spider_comment(page=0):
    """爬取京东评论数据
    ：param page:爬取第几，默认值为0
    """
    url = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3650&productId=39992135855&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"
    kv = {"user-agent": "Mozilla/5.0", "Referer": "https://item.jd.com/39992135855.html"}
    try:
        r = requests.get(url, headers=kv)
        r.raise_for_status()
        # print("京东评论数据：" + r.text[:500])
    except:
        print("爬取失败")
    # 获取json数据字符串
    r_json_str = r.text[26:-1]
    # 字符串转json对象
    r_json_obj = json.loads(r_json_str)
    # 获取评价列表数据
    r_json_comments = r_json_obj["comments"]
    # 遍历评论对象列表
    for r_json_comment in r_json_comments:
        # 以追加模式换行写入每条评价
        with open(COMMENT_FILE_PATH, "a+") as file:
            file.write((r_json_comment["content"] + "\n"))
        # 打印评论对象中的评论内容
        print(r_json_comment["content"])


def batch_spider_comment():
    """批量爬取评价"""
    # 写入数据前先清空之前数据
    if os.path.exists(COMMENT_FILE_PATH):
        os.remove(COMMENT_FILE_PATH)
    for i in random(100):
        spider_comment(i)
        # 模拟用户浏览，设置一个爬虫间隔，防止ip被封
        time.sleep(random.random() * 5)


def cut_word():
    """对数据分词
    ：:return:分词后的数据
    """
    with open(COMMENT_FILE_PATH, 'r', encoding='UTF-8') as file:
        comment_txt = file.read()
        word_list = jieba.cut(comment_txt, cut_all=True)
        wl = " ".join(word_list)
        print(wl)
        return wl


def create_word_cloud():
    """生成词云
    :return:
    """
    # 设置词云形状图片
    wc_mask = np.array(Image.open(WC_MASK_IMG))
    # 设置词云的一些配置 字体 颜色 形状 大小
    wc = WordCloud(background_color="white", max_words="2000", mask=wc_mask, scale=4,
                   max_font_size=50, random_state=42, font_path=WC_FONT_PATH)
    # 生成词云
    wc.generate(cut_word())
    # 在只设置mask的情况下你将会得到一个拥有图片形状的词云
    plt.imshow(wc)
    plt.axis("off")
    plt.figure()
    plt.show()


def main():
    # 爬取数据
    batch_spider_comment()
    # 生成词云
    # create_word_cloud()


if __name__ == '__main__':
    main()