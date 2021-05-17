# -*- coding: utf-8 -*-

from scrapy import Request
from ..items import *
import random
import json
import re
import redis
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.project import get_project_settings

class NewsinaSpiderSpider(RedisSpider):
    name = 'newsina_spider'
    redis_key = 'spider:start_urls'
    
    def __init__(self, page_num=10,lid=2509,node='master',task_id='111', *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.page_num=int(page_num)
        self.lid=str(lid)
        self.task_id=task_id
        self.redis_key=self.redis_key+task_id
        base_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid={}&k=&num=50&page={}&r={}'
        if node=='master':
            settings = get_project_settings()
            r = redis.Redis(host=settings.get("REDIS_HOST"), port=settings.get("REDIS_PORT"), decode_responses=True)
            for page in range(1, self.page_num+1):
                #  按上面注释  可修改 这里"2509"代表"全部"类别的新闻
                # lid = "2509"
                rm = random.random()
                user_info_url=base_url.format(lid, page, rm)
            r.lpush(self.redis_key, user_info_url)

    # def start_requests(self):
    #     lid=self.lid
    #     for page in range(1, self.page_num+1):
    #         #  按上面注释  可修改 这里"2509"代表"全部"类别的新闻
    #         # lid = "2509"
    #         r = random.random()
    #         yield Request(self.base_url.format(lid, page, r), callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        data_list = result.get('result').get('data')
        for data in data_list:
            item = NewsinaspiderItem()

            ctime = datetime.fromtimestamp(int(data.get('ctime')))
            ctime = datetime.strftime(ctime, '%Y-%m-%d %H:%M')
            item['dataType']=3
            item['ctime'] = ctime
            item['url'] = data.get('url')
            try:
                item['img'] = data.get('img')
            except:
                continue
            item['title'] = data.get('title')
            item['media_name'] = data.get('media_name')
            item['keywords'] = data.get('keywords')
            yield Request(url=item['url'], callback=self.parse_content, meta={'item': item})

    # 进入到详情页面 爬取新闻内容
    def parse_content(self, response):
        item =response.meta['item']
        content = ''.join(response.xpath('//*[@id="artibody" or @id="article"]//p/text()').extract())
        content = re.sub(r'\u3000', '', content)
        content = re.sub(r'[ \xa0?]+', ' ', content)
        content = re.sub(r'\s*\n\s*', '\n', content)
        content = re.sub(r'\s*(\s)', r'\1', content)
        content = ''.join([x.strip() for x in content])

        # content_list = response.xpath('//*[@id="artibody" or @id="article"]//p/text()').extract()
        # content = r""
        # for part in content_list:
        #     part = part.strip()
        #     content += part

        item['content'] = content
        yield item




