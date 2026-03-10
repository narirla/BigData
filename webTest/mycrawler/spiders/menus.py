import scrapy
from bs4 import BeautifulSoup
import re
from mycrawler.items import MyMenu

class MenusSpider(scrapy.Spider):
    name = "menus"
    allowed_domains = ["www.menupan.com"]
    start_urls = ["http://www.menupan.com/restaurant/bestrest/bestrest.asp?pt=rt&areacode=bs205"]

    def parse(self, response):
        html_content = response.body
        html = BeautifulSoup( html_content, 'html.parser')
        
        for li in html.select( '.rankingList li'):
            rank = li.select_one( '.numTop, .rankNum').string 
            restName= li.select_one('.restName > a').string
            listType =  li.select_one('.listType').string 
            print(rank)
            print(restName)
            print(listType)
            yield MyMenu(rank=rank, restName=restName,listType=listType)
            
            # item={}
            # item['rank'] = rank
            # item['restName'] = restName
            # item['listType'] = listType
            # yield item

 

