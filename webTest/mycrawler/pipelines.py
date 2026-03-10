# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
# pipelines.py

class SimplePrintPipeline:
    def process_item(self, item, spider):
        print(">>> ITEM:", item)
        return item
    
class ExcelExportPipeline:
    def __init__(self):
        self.data = []

    def process_item(self, item, spider):
        print('excel process_item')
        self.data.append(dict(item))
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.data)
        df.to_excel('asset/output.xlsx', index=False)


class MycrawlerPipeline:
    def process_item(self, item, spider):
        return item
