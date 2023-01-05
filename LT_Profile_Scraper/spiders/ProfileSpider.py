import scrapy
from ..items import Profile
from .tools.ContactParser import ContactParser
import pandas as pd


class ProfileSpider(scrapy.Spider):

    def __init__(self):
        self.name = "profile"
        self.setting = pd.read_csv("input/setting.csv")
        self.CP = ContactParser()

    def start_requests(self):
        links_df = pd.read_csv("output/links.csv")
        for index, row in links_df.iterrows():
            yield scrapy.Request(
                url=row["link"],
                callback=self.parse,
                cb_kwargs={"firm": row["firm"]},
            )

    def parse(self, response, firm):
        name_css = self.setting.loc[self.setting["firm"] == firm]["name_css"].values[0]
        name = self.parse_name(response=response, name_css=name_css)
        #
        # section css
        #
        section = self.setting.loc[self.setting["firm"] == firm]["section_css"].values[0]
        if section != "empty":
            if section[0] == "/" or section[0] == "(":
                html = str(response.xpath(section).get())
            elif section[0] == "c":
                if "contains" not in section:
                    new_css = section
                    new_css = new_css.replace("concat", "")
                    new_css = new_css.replace(",", "|")
                    html = str(response.xpath(new_css).get())
                else:
                    html = str(response.xpath(section).get())
            else:
                html = str(response.css(section).get())
        else:
            html = str(response.body)
        #
        # data load
        #
        load_item = {
            # id
            "Url": response.url,
            "Firm": firm,
            "Firm_URL": self.setting.loc[self.setting["firm"] == firm]["firm_url"].values[0],
            "Name": name,
            # data
            "Phone": self.CP.parse_phone(html, mobile=False),
            "Mobile": self.CP.parse_phone(html, mobile=True),
            "Email": self.CP.parse_email(html=html, name=name),
            "Linkedin": self.CP.parse_linkedin(html),
            "Title": "null",
            "Bio": "null",
            "Sector": "null"
        }
        item = Profile()
        item["Sector"] = load_item["Sector"]
        item["Url"] = load_item["Url"]
        item["Firm"] = load_item["Firm"]
        item["Firm_URL"] = load_item["Firm_URL"]
        item["Phone"] = load_item["Phone"]
        item["Mobile"] = load_item["Mobile"]
        item["Email"] = load_item["Email"]
        item["Linkedin"] = load_item["Linkedin"]
        item["Name"] = load_item["Name"]
        item["Title"] = load_item["Title"]
        item["Bio"] = load_item["Bio"]
        yield item

    @staticmethod
    def parse_name(response, name_css):
        if name_css[0] == "/" or name_css[0] == "(":
            try:
                name = response.xpath(f"{name_css}/text()[normalize-space()]").get()
            except Exception as e:
                print(e)
                return None
        elif name_css[0] == "c":
            try:
                name = response.xpath(f"{name_css}").get()
            except Exception as e:
                print(e)
                return None
        elif name_css[0:6] == "%title":
            try:
                sep = name_css[6:].split('"')[1]
                pos = name_css[6:].split('%')[1]
                name = response.xpath("//title/text()").get()
                name = name.split(sep)[int(pos)]
            except Exception as e:
                print(e)
                return None
        else:
            try:
                name = response.css(f"{name_css}::text").get()
            except Exception as e:
                print(e)
                return None

        if name:
            try:
                name = name.strip()
                name = ' '.join(name.split())
                return name
            except Exception as e:
                print(e)
                return None
        else:
            return None
