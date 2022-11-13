from selenium import webdriver
from const import DRIVER_PATH, URL, HTML_PATH
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utils import write_file
import time
import os
from supabase import create_client
from dotenv import load_dotenv
import boto3

load_dotenv()

# SUPABASE_URL = "https://bygyxaadwcmznscegtgm.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5Z3l4YWFkd2Ntem5zY2VndGdtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NjYwMTc4MDMsImV4cCI6MTk4MTU5MzgwM30.BA86-BFW0Zela8peTElpoK3VTZzkBQs02d12bYQqer4"
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"

client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-east-1'
)


class Selenium:
    def __init__(self, options=None, executable_path=None):
        if options is None:
            options = Options()
            options.headless = True
            options.binary_location = GOOGLE_CHROME_BIN
            options.add_argument("--lang=en-GB")

        if executable_path is None:
            executable_path = CHROMEDRIVER_PATH
        self.driver = webdriver.Chrome(options=options, executable_path=executable_path)

    def get_page(self, url=None, page=1):
        if not url:
            url = URL
        url += f"&start={(page - 1) * 10}"
        print("\n- - - Scraping {} - - -\n".format(url))
        self.driver.get(url)
        return self.driver

    def save_screenshot_to_s3(self):
        self.driver.save_screenshot('ss.jpg')
        client.upload_file('ss.jpg', 'genie-public-user-data', 'ss.jpg')

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


class Supabase:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def sign_up(self, email: str, password: str):
        return self.client.auth.sign_up(email=email, password=password)

    def sign_in(self, email: str, password: str):
        return self.client.auth.sign_in(email=email, password=password)

    def sign_out(self):
        return self.client.auth.sign_out()

    def insert(
        self, table, uuid, key_value, search_key, search_location, status, upsert=False
    ):
        params = {
            "uuid": uuid,
            "data_json": key_value,
            "search_key": search_key,
            "search_location": search_location,
            "status": status,
        }
        response = self.client.table(table).insert(params).execute()
        return response.data

    def update(self, table, uuid, key_value, status):
        params = {"data_json": key_value, "status": status}
        response = self.client.table(table).update(params).eq("uuid", uuid).execute()
        return response.data

    def select_all(self, table: str, columns: list):
        columns = "*" if not len(columns) else ",".join(columns)
        response = self.client.table(table).select(columns).execute()
        return response.data

    def select_by_uuid(self, table: str, columns: list, data_uuid):
        columns = "*" if not len(columns) else ",".join(columns)
        if data_uuid:
            response = (
                self.client.table(table).select(columns).eq("uuid", data_uuid).execute()
            )
        return response.data

    def select_by(
        self, table: str, columns: list, search_key: str, search_location: str
    ):
        columns = "*" if not len(columns) else ",".join(columns)
        if search_key and not search_location:
            response = (
                self.client.table(table)
                .select(columns)
                .eq("search_key", search_key)
                .execute()
            )
        elif not search_key and search_location:
            response = (
                self.client.table(table)
                .select(columns)
                .eq("search_location", search_location)
                .execute()
            )
        else:
            response = (
                self.client.table(table)
                .select(columns)
                .eq("search_key", search_key)
                .eq("search_location", search_location)
                .execute()
            )
        return response.data


def init_selenium(url=URL, quit=True, page=1, destination=""):
    driver = Selenium()
    driver.get_page(url, page)
    # driver.save_screenshot_to_s3()
    driver.click_related_question()
    driver.download_page(destination)
    if quit:
        driver.quit()
    return driver
