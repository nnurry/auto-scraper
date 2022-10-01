from selenium import webdriver
from const import DRIVER_PATH, URL, HTML_PATH
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def _path(name):
    return "./data/" + name


def outer(func):
    def inner(*args, **kwargs):
        fn_call = func(*args, **kwargs)
        print("Result of {}:\n{}\n\n\n\n".format(func.__name__, fn_call))
        return fn_call

    return inner


def write_file(content, filepath, mode="w", encoding="utf-8"):
    with open(filepath, mode, encoding=encoding) as f:
        f.write(content)
    return content


class Selenium:
    def __init__(self, options=None, executable_path=None):
        if options is None:
            options = Options()
            options.headless = True
            options.add_argument("--window-size=1920,1080")
        if executable_path is None:
            executable_path = DRIVER_PATH
        self.driver = webdriver.Chrome(options=options, executable_path=executable_path)

    def get_page(self, url=None):
        if not url:
            url = URL
        self.driver.get(url)
        return self.driver

    def click_related_question(self):
        elements = self.driver.find_elements(By.ID, "lSI4Y4W7Mv_V2roPq--D2AE__3")
        [element.click() for element in elements]
        return self.driver

    def download_page(self):
        return write_file(self.driver.page_source, HTML_PATH)

    def quit(self):
        self.driver.quit()
