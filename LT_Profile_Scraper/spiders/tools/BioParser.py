import pandas as pd
import re


class BioParser:
    def __init__(self):
        self.titles = pd.read_csv("input/titles.csv", encoding="latin-1")
        self.titles_long = pd.read_csv("input/titles_long.csv", encoding="latin-1")
        self.titles = self.titles.rename(columns={"ï»¿title": "title"})
        self.titles_long = self.titles_long.rename(columns={"ï»¿title": "title"})

    @staticmethod
    def parse_name(response, name_css):
        if name_css[0] == "/" or name_css[0] == "(":
            if "text()" in name_css:
                try:
                    name = response.xpath(f"{name_css}").get()
                except Exception as e:
                    print(e)
                    return None
            else:
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

    def parse_title(self, response, css):
        for css_ in css:
            if css_ == "!!empty":
                continue
            elif "/text()" in css_:
                try:
                    title = response.xpath(f"{css_}").get()
                except Exception as e:
                    print(e)
                    continue
            elif css_[0] == "/" or css_[0] == "(":
                try:
                    title = response.xpath(f"{css_}/text()[normalize-space()]").get()
                except Exception as e:
                    print(e)
                    continue
            else:
                try:
                    title = response.css(f"{css_}::text").get()
                except Exception as e:
                    print(e)
                    continue
            if title:
                try:
                    for index, row in self.titles_long.iterrows():
                        if any(re.findall(rf"{row['title']}", title, re.IGNORECASE)):
                            return row["title"]
                    for index, row in self.titles.iterrows():
                        if any(re.findall(rf"{row['title']}", title, re.IGNORECASE)):
                            return row["title"]
                except Exception as e:
                    print(e)
            else:
                continue
        return None
