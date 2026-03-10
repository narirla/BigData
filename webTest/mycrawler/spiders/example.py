import scrapy
from mycrawler.items import MyItem;


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response):
        title=response.css("h1::text").get(),
        url=response.url
        print(title)
        print(url)
        yield MyItem(title=title,url=url)
