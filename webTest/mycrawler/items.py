# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyMenu(scrapy.Item):
    rank = scrapy.Field()
    restName = scrapy.Field()
    listType = scrapy.Field()

class MyItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()

class MycrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
