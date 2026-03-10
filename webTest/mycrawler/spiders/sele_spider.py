from pathlib import Path

import scrapy

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class SeleSpider(scrapy.Spider):
    name = "sele"

    def set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                options=chrome_options)
        return driver

    def start_requests(self):
        driver = self.set_chrome_driver()
        murl ="http://www.menupan.com/restaurant/bestrest/bestrest.asp?pt=rt&areacode=ss201" 
        driver.get(murl)

        body = driver.page_source
        driver.quit()

        yield scrapy.Request(url=murl, body=body, callback=self.parse)

    def parse(self, response):
        
        lis = response.css( '.rankingList > .list > li')
        
        for li in lis:
            rank = li.css('.numTop::text, .rankNum::text').get()
            restName = li.css( '.restName > a::text').get()
            listType = li.css( '.listType::text').get()
            print( rank)
            print( restName)
            print( listType)
            item ={}
            item['rank'] = rank+"*"
            item['restName'] = restName
            item['listType'] = listType
            print('item============>', item)
            yield item 