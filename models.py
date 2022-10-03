from selenium import webdriver
from const import DRIVER_PATH, URL, HTML_PATH
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utils import write_file
import time


class Selenium:
    def __init__(self, options=None, executable_path=None):
        if options is None:
            options = Options()
            options.headless = True
            options.add_experimental_option(
                'prefs', {'intl.accept_languages': 'en-GB'})

        if executable_path is None:
            executable_path = DRIVER_PATH
        self.driver = webdriver.Chrome(
            options=options, executable_path=executable_path)

    def get_page(self, url=None, page=1):
        if not url:
            url = URL
        self.driver.get(url + f'&start={(page - 1) * 10}')
        return self.driver

    def click_related_question(self, xpath="//div[@jsname = 'Cpkphb']"):
        tries = 1

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

    def download_page(self, destination=HTML_PATH):
        return write_file(self.driver.page_source, destination, "w", "utf-8")

    def quit(self):
        self.driver.quit()


def init_selenium(quit=True, page=1, destination=''):
    driver = Selenium()
    driver.get_page(URL, page)
    driver.click_related_question()
    driver.download_page(destination)
    if quit:
        driver.quit()
    return driver
