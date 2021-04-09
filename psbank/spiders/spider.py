import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PpsbankItem
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
pattern = r'(\xa0)?'

class PpsbankSpider(scrapy.Spider):
	name = 'psbank'
	page = 1
	start_urls = ['https://www.psbank.net/news/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="jump"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 5:
			yield FormRequest.from_response(response, formdata={
				"__EVENTTARGET": f'ctl00$content$ctl00$lvNews$DataPager$ctl00$ctl0{self.page}'}, callback=self.parse)
			self.page += 1

	def parse_post(self, response):
		date = response.xpath('//span[@class="pubdate"]/text()').get()
		title = response.xpath('//span[@id="content_ctl00_lblTitle"]/text()').get()
		content = response.xpath('//div[@class="news-detail-copy"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PpsbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
