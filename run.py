from LT_Profile_Scraper.spiders.ProfileSpider import ProfileSpider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from LT_Profile_Scraper import settings as my_settings
from LinkLoader import LinkLoader

L = LinkLoader()
L.start()

crawler_settings = Settings()
crawler_settings.setmodule(my_settings)
profile_crawl = CrawlerProcess(settings=crawler_settings)
profile_crawl.crawl(ProfileSpider)
profile_crawl.start()
