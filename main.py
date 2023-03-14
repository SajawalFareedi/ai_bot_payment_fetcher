from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup as bs4

import selenium.webdriver.support.expected_conditions as EC
import undetected_chromedriver as uc

from time import sleep
from random import randrange


class PaymentProviderFetcher():
    def __init__(self):
        self.PAYMENT_GATEWAYS = open("payment_gateways.txt", encoding="utf8").read().strip().lower().split('\n')
        self.WEBSITES = open("urls.txt", encoding="utf8").read().strip().lower().split("\n")

        self.headless = False
        self.driver: WebDriver

    def init_webdriver(self):
        # undetected_chromedriver
        options = uc.ChromeOptions()
        options.add_argument("--log-level=4")
        options.add_argument('--profile-directory=Default')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        # todo: this param shows a warning in chrome head-full
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-dev-shm-usage')
        # this option removes the zygote sandbox (it seems that the resolution is a bit faster)
        options.add_argument('--no-zygote')
        # options.add_argument("--lang=en")

        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1,
            "excludeSwitches": ["enable-automation", "disable-popup-blocking"],
            'useAutomationExtension': False,
            # "translate_whitelists": {"da": "en-US"},
            # "translate": {"enabled": "true"}
        })

        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {"performance": "ALL"}

        self.driver = uc.Chrome(options=options, desired_capabilities=capabilities, headless=self.headless)

        self.driver.maximize_window()
        self.driver.set_page_load_timeout(120)
    
    def find_product_on_main_page(self, website: str):
        self.driver.get(website)
    
    def get_product(self, website: str):
        self.driver.get(f"{website}/robots.txt")
        
        if self.driver.current_url.find("robots") == -1:
            self.driver.get(f"{website}/sitemap.xml")
            if self.driver.current_url.find("sitemap") == -1:
                self.find_product_on_main_page(website)
            
    
    def add_product_to_cart(self, website: str):
        added_to_cart = False
        hrefs = []
        
        html = self.driver.page_source
        soup = bs4(html, features="lxml")
        
        for a_tag in soup.find_all("a", {"href": True}):
            a = a_tag["href"].lower()
            if a.lower().find("product") != -1 or a.find("produkt") != -1:
                if a.startswith("/"):
                    hrefs.append(f"{website}{a}")
                else:
                    hrefs.append(a)
        
        hrefs = list(set(hrefs))
        
        if len(hrefs) == 0:
            for a_tag in soup.find_all("a", {"href": True}):
                a = a_tag["href"].lower()
                if a.startswith("/"):
                    hrefs.append(f"{website}{a}")
                else:
                    hrefs.append(a)
        
        for href in hrefs:
            self.driver.get(href)
            sleep(1.2)
            
            try:
                add_to_cart = self.driver.find_element(By.XPATH, "//*[text()='']")
                # * Tilføj til kurv
                # * Læg i kurv
                # * Add to cart
                # * Tilføj til indkøbskurv
                # * Tilføj til kurv
            except:
                add_to_cart = None
                
            if not add_to_cart:
                continue
            
            self.driver.execute_script("arguments[0].click();", add_to_cart)
            added_to_cart = True
            break

    def do_checkout(self):
        ...

    def start_main_process(self):
        for website in self.WEBSITES:
            website = f"https://{website}"
            print(f"Current Website: {website}")
            
            self.driver.get(website)
            sleep(6.7)
            
            self.get_product(website=website)
            self.add_product_to_cart(website=website)
            self.do_checkout()
            break

    def main(self):
        self.init_webdriver()
        sleep(1.3)
        self.start_main_process()
        sleep(3.2)
        self.driver.quit()


if __name__ == "__main__":
    model = PaymentProviderFetcher()
    model.main()
