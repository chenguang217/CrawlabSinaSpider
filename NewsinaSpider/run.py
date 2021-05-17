from scrapy import cmdline
cmdline.execute('scrapy crawl newsina_spider'.split())
# cmdline.execute('scrapy crawl newsina_slavespider -a page_num=1 -a lid=2509'.split())
 
    #     "2509": "全部",
    #     "2510": "国内",
    #     "2511": "国际",
    #     "2669": "社会",
    #     "2512": "体育",
    #     "2513": "娱乐",
    #     "2514": "军事",
    #     "2515": "科技",
    #     "2516": "财经",
    #     "2517": "股市",
    #     "2518": "美股",
    #     "2968": "国内_国际",
    #     "2970": "国内_社会",
    #     "2972": "国际_社会",
    #     "2974": "国内国际社会"

#
    #分布式   关键字   参数json  https://news.sina.com.cn/roll/#pageid=153&lid=2510&etime=1619798400&stime=1619884800&ctime=1619884800&date=2021-05-01&k=&num=50&page=1