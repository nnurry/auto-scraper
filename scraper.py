from autoscraper import AutoScraper
import json
from const import organic, local, ads, related
from utils import _path, outer, write_file
class Scraper:
    def __init__(self):
        self.scraper = AutoScraper()
            
    def ingest(self, html, data):
        for wanted_list in data:
            self.scraper.build(html=html, wanted_list=wanted_list)

    
    def get_result(self, html, filename, format=".json"):
        result = self.scraper.get_result_similar(html=html, grouped=True)
        return write_file(json.dumps(result), filename + format)
    

@outer
def get_related():
    scraper = Scraper()

    related.pop('url')

    scraper.ingest(**related)
    return scraper.get_result(related["html"], _path("related"))

@outer   
def get_organic():
    scraper = Scraper()

    organic.pop('url')

    scraper.ingest(**organic)
    return scraper.get_result(organic["html"], _path("organic"))
    
@outer
def get_ads():
    scraper = Scraper()

    ads.pop('url')

    scraper.ingest(**ads)
    return scraper.get_result(ads["html"], _path("ads"))

@outer  
def get_local():
    scraper = Scraper()

    local.pop('url')

    scraper.ingest(**local)
    return scraper.get_result(local["html"], _path("local"))


def get_data():
    get_organic()
    get_local()
    get_ads()
    get_related()