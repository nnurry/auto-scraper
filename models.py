from selenium import webdriver
from const import DRIVER_PATH, URL, HTML_PATH, organic, local, ads, related
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utils import write_file, outer, _path
from autoscraper import AutoScraper
import json
from pathlib import Path
import time


class Selenium:
    def __init__(self, options=None, executable_path=None):
        if options is None:
            options = Options()
            # options.headless = True
        if executable_path is None:
            executable_path = DRIVER_PATH
        self.driver = webdriver.Chrome(options=options, executable_path=executable_path)

    def get_page(self, url=None):
        if not url:
            url = URL
        self.driver.get(url)
        return self.driver

    def click_related_question(self, xpath="//div[@jsname = 'Cpkphb']"):
        tries = 2
        def mass_click():
            elements = self.driver.find_elements(By.XPATH, xpath)
            for element in elements:
                element.click()
                time.sleep(0.25)
        for i in range(0, tries):
            mass_click()
        time.sleep(1)
        return self.driver

    def save_screenshot(self, filepath="./screenshot.png"):
        self.driver.save_screenshot(filepath)
        return True

    def download_page(self):
        return write_file(self.driver.page_source, HTML_PATH)

    def quit(self):
        self.driver.quit()


class Scraper:
    def __init__(self):
        self.scraper = AutoScraper()

    def ingest(self, data, html, url=""):
        for wanted_list in data:
            self.scraper.build(html=html, wanted_list=wanted_list)

    def get_result(self, html, filename, format=".json"):
        result = self.scraper.get_result_similar(html=html, grouped=True)
        return write_file(json.dumps(result), filename + format)


class Execute:
    @staticmethod
    def init_selenium(quit=True):
        driver = Selenium()
        driver.get_page()
        driver.click_related_question()
        driver.download_page()
        if quit:
            driver.quit()
        return driver

    @staticmethod
    def get_file(filepath=HTML_PATH):
        return Path(filepath).read_text(encoding="utf-8")

    @staticmethod
    @outer
    def get_related(filepath=HTML_PATH):
        scraper = Scraper()
        html = Execute.get_file(filepath)
        related.update(dict(html=html))
        scraper.ingest(**related)
        return scraper.get_result(related["html"], _path("related"))

    @staticmethod
    @outer
    def get_organic(filepath=HTML_PATH):
        scraper = Scraper()
        html = Execute.get_file(filepath)
        organic.update(dict(html=html))
        scraper.ingest(**organic)
        return scraper.get_result(organic["html"], _path("organic"))

    @staticmethod
    @outer
    def get_ads(filepath=HTML_PATH):
        scraper = Scraper()
        html = Execute.get_file(filepath)
        ads.update(dict(html=html))
        scraper.ingest(**ads)
        return scraper.get_result(ads["html"], _path("ads"))

    @staticmethod
    @outer
    def get_local(filepath=HTML_PATH):
        scraper = Scraper()
        html = Execute.get_file(filepath)
        local.update(dict(html=html))
        scraper.ingest(**local)
        return scraper.get_result(local["html"], _path("local"))
