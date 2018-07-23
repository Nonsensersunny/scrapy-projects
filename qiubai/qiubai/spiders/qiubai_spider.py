# -*- coding: utf-8 -*-
import scrapy
from qiubai.items import QiubaiItem


class QiubaiSpiderSpider(scrapy.Spider):
    name = 'qiubai_spider'
    allowed_domains = ['qiushibaike.com']
    start_urls = ['https://www.qiushibaike.com']

    def parse(self, response):
        article_list = response.xpath("//div[@class='col1']/div")
        for item in article_list:
            qiubai_item = QiubaiItem()
            qiubai_item['author'] = item.xpath(".//div[@class='author clearfix']//h2/text()").extract_first()
            qiubai_item['content'] = item.xpath(".//div[@class='content']/span/text()").extract_first()
            qiubai_item['likes'] = item.xpath(".//span[@class='stats-vote']//i[@class='number']/text()").extract_first()
            qiubai_item['comment_num'] = item.xpath(".//span[@class='stats-comments']//i[@class='number']/text()").extract_first()
            qiubai_item['best_comment'] = item.xpath(".//div[@class='main-text']/text()").extract_first()
            # print(qiubai_item)
            yield qiubai_item

        next_link = response.xpath("//ul[@class='pagination']/li[last()]/a/@href").extract()
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://www.qiushibaike.com" + next_link, callback=self.parse)