from bs4 import BeautifulSoup


class BioParser:
    def __init__(self):
        self.data = ''

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.text
