# -*- coding: utf-8 -*-

from scrapy import Request
from ..items import *
import random
import json
import re
import redis
import requests
import logging
import time
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.project import get_project_settings
from distutils.util import strtobool
import os
from urllib.request import urlretrieve


class NewsinaSpiderSpider(RedisSpider):
    name = 'newsina_spider'
    redis_key = 'spider:start_urls'

    def __init__(self, page_num=50, lid=2509, node='master', uu_id='111', crawl_image='False', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_num = int(page_num)
        self.lid = str(lid)
        self.task_id = uu_id
        self.redis_key = self.redis_key + uu_id
        self.crawl_image = strtobool(crawl_image)

        if not os.path.exists('/data/'):
            os.makedirs('/data/')

        if node == 'master':
            base_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid={}&k=&num=50&page={}&r={}'
            settings = get_project_settings()
            r = redis.Redis(host=settings.get("REDIS_HOST"), port=settings.get("REDIS_PORT"), decode_responses=True)
            for page in range(1, self.page_num + 1):
                #  按上面注释  可修改 这里"2509"代表"全部"类别的新闻
                # lid = "2509"
                rm = random.random()
                user_info_url = base_url.format(lid, page, rm)
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

            item['task_id'] = self.task_id
            item['uu_id'] = self.task_id
            ctime0 = datetime.fromtimestamp(int(data.get('ctime')))
            ctime = datetime.strftime(ctime0, '%Y-%m-%d_%H:%M')
            item['dataType'] = 3
            item['ctime'] = ctime
            item['url'] = data.get('url')
            # try:
            #     item['img'] = data.get('img')
            # except:
            #     continue
            item['title'] = data.get('title')
            item['media_name'] = data.get('media_name')
            item['keywords'] = data.get('keywords')

            # 下载图片
            pic_list = []
            if(self.crawl_image):
                i = 0
                for u in data.get('images'):
                    i = i + 1
                    pic_url = u['u']
                    file_name = self.task_id + '_' + data.get('docid')[6:] + '_' + str(i) + '.jpg'
                    urlretrieve(pic_url, '/data/' + file_name)
                    try:
                        self.fileUpload('/data/' + file_name, file_name)
                    except:
                        logging.log(msg=time.strftime("%Y-%m-%d %H:%M:%S [WeiboSpider] ")
                                        + "newsina_spider" + ": failed to upload image:"
                                        + file_name, level=logging.INFO)
                    pic_list.append('/data/' + file_name)
            item['pics'] = pic_list

            yield Request(url=item['url'], callback=self.parse_content, meta={'item': item})

    # 进入到详情页面 爬取新闻内容
    def parse_content(self, response):
        item = response.meta['item']
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

    def fileUpload(self, file_path, file_name):
        upload_url = 'http://192.168.0.230:8888/upload'
        header = {"ct": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        files = {'file': open(file_path, 'rb')}
        # upload_data = {"parentId": "", "fileCategory": "personal", "fileSize": 179, "fileName": file_name, "uoType": 1}
        upload_data = {"fileName": file_name}
        upload_res = requests.post(upload_url, upload_data, files=files, headers=header)