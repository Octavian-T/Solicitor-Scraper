from bs4 import BeautifulSoup


class BioParser:
    def __init__(self):
        self.data = ''

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

    @staticmethod
    def parse_title(response, css):
        if css[0] == "/" or css[0] == "(":
            try:
                title = response.xpath(f"{css}/text()[normalize-space()]").get()
            except Exception as e:
                print(e)
                return None
        elif css[0] == "c":
            try:
                title = response.xpath(f"{css}").get()
            except Exception as e:
                print(e)
                return None
        else:
            try:
                title = response.css(f"{css}::text").get()
            except Exception as e:
                print(e)
                return None

        if title:
            try:
                title = title.strip()
                title = ' '.join(title.split())
                return title
            except Exception as e:
                print(e)
                return None
        else:
            return None
