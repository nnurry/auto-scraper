from autoscraper import AutoScraper
import json
from const import organic, local, ads, related
from utils import _path, outer

class Scraper:
    def __init__(self):
        self.scraper = AutoScraper()

    def ingest_url(self, url, data):
        for wanted_list in data:
            self.scraper.build(url=url, wanted_list=wanted_list)
            
    def ingest_html(self, html, data):
        for wanted_list in data:
            self.scraper.build(html=html, wanted_list=wanted_list)

    @outer
    def get_result_url(self, url, filename, format=".json"):
        result = self.scraper.get_result_similar(url=url, grouped=True)

        with open(filename + format, "w") as f:
            f.write(json.dumps(result))
        return result
    
    @outer
    def get_result_html(self, html, filename, format=".json"):
        result = self.scraper.get_result_similar(html=html, grouped=True)

        with open(filename + format, "w") as f:
            f.write(json.dumps(result))
        return result


def related_html():
    scraper = Scraper()

    related.pop('url')

    scraper.ingest_html(**related)
    scraper.get_result_html(related["html"], _path("related"))
    
def organic_html():
    scraper = Scraper()

    organic.pop('url')

    scraper.ingest_html(**organic)
    scraper.get_result_html(organic["html"], _path("organic"))
     
def ads_html():
    scraper = Scraper()

    ads.pop('url')

    scraper.ingest_html(**ads)
    scraper.get_result_html(ads["html"], _path("ads"))
    
def local_html():
    scraper = Scraper()

    local.pop('url')

    scraper.ingest_html(**local)
    scraper.get_result_html(local["html"], _path("local"))
    

def related_url():
    scraper = Scraper()

    related.pop('html')

    scraper.ingest_url(**related)
    scraper.get_result_url(related["url"], _path("related"))
    
def organic_url():
    scraper = Scraper()

    organic.pop('html')

    scraper.ingest_url(**organic)
    scraper.get_result_url(organic["url"], _path("organic"))
     
def ads_url():
    scraper = Scraper()

    ads.pop('html')

    scraper.ingest_url(**ads)
    scraper.get_result_url(ads["url"], _path("ads"))
    
def local_url():
    scraper = Scraper()

    local.pop('html')

    scraper.ingest_url(**local)
    scraper.get_result_url(local["url"], _path("local"))

def get_data_by_html():
    organic_html()
    local_html()
    ads_html()
    related_html()
    
def get_data_by_url():
    organic_url()
    local_url()
    ads_url()
    related_url()
