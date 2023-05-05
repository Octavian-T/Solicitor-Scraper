# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class Profile(Item):
    Url = Field()
    Phone = Field()
    Mobile = Field()
    Email = Field()
    Linkedin = Field()
    Name = Field()
    Firm = Field()
    Firm_URL = Field()
    Title = Field()
    Bio = Field()
    Sector = Field()
