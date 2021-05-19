# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class NewsinaspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    collection = 'newsina'
#和字典很相似，类似于字典的字段
    dataType = Field()
    ctime = Field()  # 发布时间
    url = Field()
    img = Field()
    title = Field()  # 新闻标题
    media_name = Field()  # 发发布的媒体
    keywords = Field()  #  关键词
    content = Field()  #  新闻内容

