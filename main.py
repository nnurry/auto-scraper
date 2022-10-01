from scraper import get_data
from os import system
from utils import Selenium
from sys import argv
def init_selenium(quit=True):
    driver = Selenium()
    driver.get_page()
    driver.click_related_question()
    driver.download_page()
    if quit:
        driver.quit()
    return driver

if __name__ == '__main__':
    system('cls')
    if len(argv) > 1:
        if argv[1] == 'fetch':
            init_selenium()
    get_data()
    print("End of __main__")