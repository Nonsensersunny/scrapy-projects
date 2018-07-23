# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem 

class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        # print(response.text)
        movie_list = response.xpath("//div[@class='article']//ol[@class='grid_view']/li")
        for item in movie_list:
            douban_item = DoubanItem()
            douban_item['serial_number'] = item.xpath(".//div[@class='item']//em/text()").extract_first()
            douban_item['movie_name'] = item.xpath(".//div[@class='info']//span[@class='title']/text()").extract_first()
            douban_item['introduce'] = "".join(item.xpath(".//div[@class='info']//div[@class='bd']/p/text()").extract_first().split())
            douban_item['star'] = item.xpath(".//div[@class='info']//div[@class='bd']//div[@class='star']/span[@class='rating_num']/text()").extract_first()
            douban_item['evaluate'] = item.xpath(".//div[@class='info']//div[@class='bd']//div[@class='star']/span[last()]/text()").extract_first()
            douban_item['describe'] = item.xpath(".//div[@class='info']//div[@class='bd']//p[@class='quote']/span[@class='inq']/text()").extract_first()
            
            # print(douban_item)
            yield douban_item

        next_link = response.xpath("//div[@class='paginator']//span[@class='next']/link/@href").extract()
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/top250" + next_link, callback=self.parse)