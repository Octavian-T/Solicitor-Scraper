from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from ProfileSpider.spiders.ProfileSpider import ProfileSpider
from ProfileSpider import settings as my_settings
from ProfileLinkSpider import ProfileLinkSpider

L = ProfileLinkSpider()
L.start()

crawler_settings = Settings()
crawler_settings.setmodule(my_settings)
profile_crawl = CrawlerProcess(settings=crawler_settings)
profile_crawl.crawl(ProfileSpider)
profile_crawl.start()

# STATUS
# STATUS
# STATUS
        # Check if sending to LT
# STATUS
# STATUS
# STATUS