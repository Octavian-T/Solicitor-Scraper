from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from urllib.parse import urlparse
import time


class ProfileLinkSpider:
    def __init__(self):
        # driver
        self.driver = webdriver.Firefox()

        # load input data
        directory = pd.read_csv("input/directory.csv", encoding="latin-1")
        self.directory = directory.sample(frac=1)
        # self.directory = directory
        self.setting = pd.read_csv("input/setting.csv", encoding="latin-1")
        self.stop = pd.read_csv("input/stop_link.csv", encoding="latin-1")["link"]

        # initiate data output
        self.stats = pd.DataFrame(self.setting["firm"], columns=["firm", "links"]).fillna(0)
        self.links = []
        self.links_df = []
        self.newLinks = 0

    def start(self, debug=False):
        # load urls
        for index, url in self.directory.iterrows():
            try:
                self.driver.get(url[1])
                time.sleep(2)
            except Exception as e:
                print("error: could not load url")
                print(e)
                continue
            else:
                self.handle(url)
            if debug:
                if input("continue? ") == "":
                    continue
        self.driver.close()

    def handle(self, url):

        # prepare page, usually cookies
        before = self.setting.loc[self.setting["firm"] == url[0]]["before"].values[0]
        if before != "empty":
            try:
                if before[0] == "/" or before[0] == "(":
                    element = WebDriverWait(self.driver, 3, 3).until(
                        ec.element_to_be_clickable((By.XPATH, before)))
                    element.click()
                else:
                    element = WebDriverWait(self.driver, 3, 3).until(
                        ec.element_to_be_clickable((By.CSS_SELECTOR, before)))
                    element.click()
            except Exception as e:
                print("error: could not click before element")
                print(e)
                pass
            else:
                time.sleep(1)
        else:
            print("error: no before element found for url")

        # scroll down to load links
        # before checking if links are present
        self.scroll_down()
        time.sleep(1)

        # check links are present (and parse into memory)
        if not self.parse_links(url):
            print("error: no links found using link css (pre iteration)")
            return False

        # run through pages as specified
        else:
            # save data to csv
            self.save(url)
            pagination = self.setting.loc[self.setting["firm"] == url[0]]["pagination"].values[0]
            if pagination:
                for i in range(1, 110):
                    print(i)
                    # load more data
                    if pagination == "click":
                        if not self.click_load(url):
                            break
                    elif pagination == "scroll":
                        if not self.scroll_load() and i != 1:
                            break

                    # after more data is loaded,
                    # parse data and check it is valid,
                    # save into memory if it is or break pagination
                    if not self.parse_links(url):
                        break
                    else:
                        # save to csv
                        self.save(url)
                # save again
                self.save(url)
            else:
                print("error: no pagination type found for url")
                return False

    def save(self, url):
        # updating number of links scraped
        links = int(self.stats.loc[self.stats["firm"] == url[0]]["links"].values[0]) + self.newLinks
        self.stats.loc[self.stats.loc[self.stats["firm"] == url[0]].index[0], ["links"]] = [links]
        # saving links
        links_df = pd.concat(self.links_df)
        links_df = links_df.sample(frac=1)
        links_df.to_csv("output/links.csv")
        # saving stats
        self.stats.to_csv("output/stats-links.csv")

    def scroll_down(self):
        try:
            self.driver.execute_script(
                f"window.scrollTo(0, {self.driver.execute_script('return document.body.scrollHeight;')});")
        except Exception as e:
            print(e)
            pass

    def click_load(self, url):
        iteration = self.setting.loc[self.setting["firm"] == url[0]]["iteration"].values[0]
        if iteration:
            self.scroll_down()
            time.sleep(1)
            try:
                # click element
                if iteration[0] == "/" or iteration[0] == "(":
                    self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 3).until(
                        ec.element_to_be_clickable((By.XPATH, iteration))))
                else:
                    self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 3).until(
                        ec.element_to_be_clickable((By.CSS_SELECTOR, iteration))))
            # if 'load more'/'next page' button disappears
            # assume end of pagination has been reached
            except NoSuchElementException:
                return False
            except Exception as e:
                print("error: could not click next/load element")
                print(e)
                return False
            else:
                # allow page to finish loading
                # before next click
                time.sleep(3)
                return True
        else:
            print("error: could not find iteration element for url")
            return False

    def scroll_load(self):
        # scroll to bottom of page
        # as it is before more data loaded
        try:
            self.scroll_down()
        except Exception as e:
            print("error: could not scroll down page")
            print(e)
            return False
        finally:
            # allow page to load
            time.sleep(3)
            # check if page end has been reached
            # meaning no more data can be downloaded
            # by scrolling
            continue_loop = False
            try:
                continue_loop = self.driver.execute_script("""
                var continue_loop = arguments[0];
                const difference = document.documentElement.scrollHeight - window.innerHeight;
                const scrollposition = document.documentElement.scrollTop;
                if (difference - scrollposition <= 2) {
                    return false;
                } else {
                    return true;
                }
                """)
            except Exception as e:
                print("error: could not determine if end of page reached")
                print(e)
                return False
            finally:
                return continue_loop

    def parse_links(self, url):
        # grab array of link elements from dom
        css = self.setting.loc[self.setting["firm"] == url[0]]["link_css"].values[0]
        try:
            if css[0] == "/" or css[0] == "(":
                elements = self.driver.find_elements(By.XPATH, css)
            else:
                elements = self.driver.find_elements(By.CSS_SELECTOR, css)
        except Exception as e:
            print(e)
            return False
        else:
            # check css worked and elements present
            if elements:
                # get href from link elements
                links = []
                for element in elements:
                    try:
                        element = element.get_attribute("href")
                        if element is None:
                            continue
                        links.append(element)
                    except Exception as e:
                        print(e)
                        return False
                links = list(set(links))

                # remove bad links
                for stop in self.stop:
                    for link in links.copy():
                        if stop in link:
                            links.remove(link)

                # format links to proper url format
                formatted_links = []
                for link in links:
                    parsed_link = urlparse(str(link))
                    if parsed_link.scheme == "":
                        parsed_link = parsed_link._replace(scheme="https")
                    if parsed_link.netloc == "":
                        parsed_link = parsed_link._replace(netloc=str(urlparse(url[1]).netloc))
                    formatted_links.append(parsed_link.geturl())
                formatted_links = list(set(formatted_links))

                # check new links scraped against
                # the links already scraped
                # if no more new links found return false
                self.newLinks = 0
                newlinks = [item for item in formatted_links if item not in self.links]
                if newlinks:
                    self.links = [*self.links, *newlinks]
                    self.newLinks = int(len(newlinks))
                    for link in newlinks:
                        self.links_df.append(
                            pd.DataFrame({
                                "link": link,
                                "firm": url[0]
                            },
                                index=[0]
                            ))
                    return True
                else:
                    return False

            else:
                return False
