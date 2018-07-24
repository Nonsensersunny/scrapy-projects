# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from douban.items import DoubanItem 
from douban.settings import APP_ID, API_KEY, SECRET_KEY
from PIL import Image
from aip import AipOcr
from scrapy import cmdline


class DoubanSpiderSpider(scrapy.Spider):
    # 爬虫的基本信息
    name = 'douban_spider'                              # 爬虫名称
    allowed_domains = ['douban.com']                    # 允许爬去的域名
    start_urls = ['https://movie.douban.com/top250']    # 爬虫入口
    # 登录接口
    login_url = 'https://www.douban.com/accounts/login'
    formEmail = '13114445016'
    formPassword = 'doubantest'
    # 主页面 用于获取captcha_id
    main_url = 'https://www.douban.com/'
    # 调用百度图片识别
    AipOcrClient = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 正则 用于剔除百度图片识别的多余的部分
    pattern = re.compile(r'\w{3,}')
    # 获取验证码的请求头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"}

    # 请求入口
    def start_requests(self):
        return [scrapy.FormRequest("https://accounts.douban.com/login", headers=DoubanSpiderSpider.headers,
                                   meta={"cookiejar": 1},
                                   callback=self.parse_before_login)]

    # 登录前解析数据，获取验证码
    def parse_before_login(self, response):
        captcha_id = response.xpath('//input[@name="captcha-id"]/@value').extract_first()
        captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
            formdata = {
                "source": "index_nav",
                "form_email": DoubanSpiderSpider.formEmail,
                "form_password": DoubanSpiderSpider.formPassword,
            }
        else:
            save_image_path = "./captcha.jpeg"
            result = requests.get(captcha_image_url)
            with open(save_image_path, 'wb') as f:
                f.write(result.content)
            image = self.get_file_content(save_image_path)
            # 通用文字识别（基础识别）
            # parseImgResult = DoubanSpiderSpider.AipOcrClient.basicGeneral(image)
            # 通用文字识别（高精度识别）
            parseImgResult = DoubanSpiderSpider.AipOcrClient.basicAccurate(image)
            print("parseImgResult: %s" % parseImgResult)
            words_result = parseImgResult['words_result']
            # 若识别得到的结果为空，则开启手动输入
            if len(words_result) == 0:
                try:
                    im = Image.open(save_image_path)
                    im.show()
                except:
                    pass
                captcha_solution = input('根据打开的图片输入验证码:')
            else:
                # 对图像识别得到的结果进行过滤
                captcha_solution = DoubanSpiderSpider.pattern.search(words_result[0]['words']).group()
            print("captcha_solution: %s" % captcha_solution)
            # 登录需要提交的表单信息
            formdata = {
                "source": "None",
                "redir": "https://www.douban.com",
                "form_email": DoubanSpiderSpider.formEmail,
                "form_password": DoubanSpiderSpider.formPassword,
                "captcha-solution": captcha_solution,
                "captcha-id": captcha_id,
                "login": "登录",
            }
            print("captcha_id: %s" % captcha_id)
            print("captcha_solution: %s" % captcha_solution)
        print("登录中")
        # 提交表单
        return scrapy.FormRequest.from_response(response, meta={"cookiejar": response.meta["cookiejar"]},
                                                formdata=formdata,
                                                callback=self.parse_after_login)

    # 登陆后解析数据
    def parse_after_login(self, response):
        print('parse_after_login')
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            print("登录失败")
            # 若图像识别失败，则通过shell重新打开本爬虫项目
            cmdline.execute('scrapy crawl douban_spider'.split())
        else:
            print(u"登录成功,当前账户为 %s" % account)
        yield from super().start_requests()

    # 保存验证码图片到本地
    def get_file_content(self, filePath):
        with open(filePath, 'rb') as f:
            return f.read()

    # 解析请求到的数据，得到进行持久化存储的数据和进一步爬取数据的请求
    def parse(self, response):
        # 一级电影条目
        movie_list = response.xpath("//div[@class='article']//ol[@class='grid_view']/li")
        for item in movie_list:
            douban_item = DoubanItem()
            douban_item['serial_number'] = item.xpath(".//div[@class='item']//em/text()").extract_first()
            douban_item['movie_name'] = item.xpath(".//div[@class='info']//span[@class='title']/text()").extract_first()
            douban_item['introduce'] = "".join(item.xpath(".//div[@class='info']//div[@class='bd']/p/text()").extract_first().split())
            douban_item['star'] = item.xpath(".//div[@class='info']//div[@class='bd']//div[@class='star']/span[@class='rating_num']/text()").extract_first()
            douban_item['evaluate'] = item.xpath(".//div[@class='info']//div[@class='bd']//div[@class='star']/span[last()]/text()").extract_first()
            douban_item['describe'] = item.xpath(".//div[@class='info']//div[@class='bd']//p[@class='quote']/span[@class='inq']/text()").extract_first()
            # 将电影条目输送至pipeline进行清洗
            yield douban_item
        # 获取下一页的链接
        next_link = response.xpath("//div[@class='paginator']//span[@class='next']/link/@href").extract()
        if next_link:
            next_link = next_link[0]
            # 将下一页的链接进行递归解析直至所有的页面的链接被遍历
            yield scrapy.Request("https://movie.douban.com/top250" + next_link, callback=self.parse)