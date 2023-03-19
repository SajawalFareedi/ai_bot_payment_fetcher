import re

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.webdriver import By

import undetected_chromedriver as uc

from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
from random import randrange
from time import sleep, time


class PaymentProviderFetcher():
    def __init__(self):
        # open("payment_gateways.txt", encoding="utf8").read().strip().lower().split('\n')
        self.PAYMENT_GATEWAYS = ["Shipmondo Payments", "Shopify Payments", "Pensopay", "Clearhaus", "Quickpay", "Bambora", "Worldline",
                                 "Reepay", "Valitor", "Freepay", "Adyen", "Farpay", "Lunar", "payments.nets", "Stripe", "Onpay", "Elevon", "Swiipe", "Paylike", "Nets"]
        self.WEBSITES = open("urls.txt", encoding="utf8").read(
        ).strip().lower().replace("\r", "").split("\n")
        self.OUTPUT_FILE = open(f"output_{time()}.txt", "w+", encoding="utf8")

        self.headless = False
        self.driver: WebDriver
        self.page_deepness = 5

    def init_webdriver(self):
        options = uc.ChromeOptions()
        options.add_argument("--log-level=4")
        options.add_argument('--profile-directory=Default')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-dev-shm-usage')
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

        self.driver = uc.Chrome(
            options=options, desired_capabilities=capabilities, headless=self.headless)

        self.driver.maximize_window()
        self.driver.set_page_load_timeout(5*60)  # 5 minutes

    def save_to_output(self, website, payment_gateway):
        file_name = self.OUTPUT_FILE.name

        with open(file_name, "a", encoding="utf8") as f:
            f.write(f"{website}\t:\t{payment_gateway}\n")

        print(f"{website}: {payment_gateway}\n")

    def is_valid_url(self, url, website) -> bool:
        url = url.replace("www.", "")

        if len(url) <= 1 or url.startswith("#"):
            return False

        if self.driver.current_url.find(url) != -1:
            return False

        if url == f"{website.lower()}/" or url == website.lower():
            return False

        if not url.startswith("/"):
            if url.find(website.lower()) == -1:
                return False

            if not url.startswith("http"):
                return False

        if url.find("blog") != -1 or url.find("kontakt") != -1 or url.find("contact") != -1 or url.find("about") != -1 or url.find("om") != -1 or url.find("/faq") != -1 or url.find("login") != -1 or url.find("konto") != -1 or url.find("account") != -1 or url.find("create") != -1 or url.find("sign") != -1 or url.find("cart") != -1 or url.find("kurv") != -1 or url.find("checkout") != -1 or url.find("tjekud") != -1 or url.find("club") != -1 or url.find("klub") != -1 or url.find("privacy") != -1 or url.find("terms") != -1 or url.find("policy") != -1:
            return False

        return True

    def get_element_by_xpath(self, xpath: str):
        return self.driver.execute_script(f"return document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;")

    def get_elements_by_xpath(self, xpath: str):
        return self.driver.execute_script(f"return document.evaluate(\"{xpath}\", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null).singleNodeValue;")

    def click_using_xpath(self, xpath: str):
        self.driver.execute_script(
            f"document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
        sleep(1.1)

    def get_element_by_css(self, css: str):
        return self.driver.execute_script(f"return document.querySelectorAll(\"{css}\")[0]")

    def execute_click_script(self, elem):
        self.driver.execute_script("arguments[0].click()", elem)

    def get_cart_btn_2(self):
        add_to_cart, x_path = None, None

        add_to_cart = self.get_element_by_xpath(
            ".//*[@value='Tilføj til kurv']")
        x_path = ".//*[@value='Tilføj til kurv']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Læg i kurv']")
            x_path = ".//*[@value='Læg i kurv']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Add to cart']")
            x_path = ".//*[@value='Add to cart']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Add to basket']")
            x_path = ".//*[@value='Add to basket']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Tilføj til indkøbskurv']")
            x_path = ".//*[@value='Tilføj til indkøbskurv']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Føj til kurv']")
            x_path = ".//*[@value='Føj til kurv']"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                ".//*[@value='Køb']")
            x_path = ".//*[@value='Køb']"

        return add_to_cart, x_path

    def get_cart_btn(self):
        add_to_cart, x_path, text = None, None, ""

        add_to_cart = self.get_element_by_xpath(
            "//*[starts-with(translate(normalize-space(), 'tilføj til kurv', 'TILFØJ TIL KURV'),'TILFØJ TIL KURV')]/*")
        x_path = "//*[starts-with(translate(normalize-space(), 'tilføj til kurv', 'TILFØJ TIL KURV'),'TILFØJ TIL KURV')]/*"
        text = "tilføj til kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'tilføj til kurv', 'TILFØJ TIL KURV'),'TILFØJ TIL KURV')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'tilføj til kurv', 'TILFØJ TIL KURV'),'TILFØJ TIL KURV')]"
            text = "tilføj til kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[translate(normalize-space(), 'læg i kurv', 'LÆG I KURV')='LÆG I KURV']/*")
            x_path = "//*[translate(normalize-space(), 'læg i kurv', 'LÆG I KURV')='LÆG I KURV']/*"
            text = "læg i kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[translate(normalize-space(), 'læg i kurv', 'LÆG I KURV')='LÆG I KURV']")
            x_path = "//*[translate(normalize-space(), 'læg i kurv', 'LÆG I KURV')='LÆG I KURV']"
            text = "læg i kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'læg i kurv', 'LÆG I KURV'),'LÆG I KURV')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'læg i kurv', 'LÆG I KURV'),'LÆG I KURV')]/*"
            text = "læg i kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'læg i kurv', 'LÆG I KURV'),'LÆG I KURV')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'læg i kurv', 'LÆG I KURV'),'LÆG I KURV')]"
            text = "læg i kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'add to cart', 'ADD TO CART'),'ADD TO CART')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'add to cart', 'ADD TO CART'),'ADD TO CART')]/*"
            text = "add to cart"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'add to cart', 'ADD TO CART'),'ADD TO CART')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'add to cart', 'ADD TO CART'),'ADD TO CART')]"
            text = "add to cart"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'add to basket', 'ADD TO BASKET'),'ADD TO BASKET')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'add to basket', 'ADD TO BASKET'),'ADD TO BASKET')]/*"
            text = "add to basket"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'add to basket', 'ADD TO BASKET'),'ADD TO BASKET')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'add to basket', 'ADD TO BASKET'),'ADD TO BASKET')]"
            text = "add to basket"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'tilføj til indkøbskurv', 'TILFØJ TIL INDKØBSKURV'),'TILFØJ TIL INDKØBSKURV')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'tilføj til indkøbskurv', 'TILFØJ TIL INDKØBSKURV'),'TILFØJ TIL INDKØBSKURV')]/*"
            text = "tilføj til indkøbskurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'tilføj til indkøbskurv', 'TILFØJ TIL INDKØBSKURV'),'TILFØJ TIL INDKØBSKURV')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'tilføj til indkøbskurv', 'TILFØJ TIL INDKØBSKURV'),'TILFØJ TIL INDKØBSKURV')]"
            text = "tilføj til indkøbskurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'føj til kurv', 'FØJ TIL KURV'),'FØJ TIL KURV')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'føj til kurv', 'FØJ TIL KURV'),'FØJ TIL KURV')]/*"
            text = "føj til kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'føj til kurv', 'FØJ TIL KURV'),'FØJ TIL KURV')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'føj til kurv', 'FØJ TIL KURV'),'FØJ TIL KURV')]"
            text = "føj til kurv"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[self::button or self::a][starts-with(translate(normalize-space(), 'køb', 'KØB'),'KØB')]/*")
            x_path = "//*[self::button or self::a][starts-with(translate(normalize-space(), 'køb', 'KØB'),'KØB')]/*"
            text = "køb"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[self::button or self::a][starts-with(translate(normalize-space(), 'køb', 'KØB'),'KØB')]")
            x_path = "//*[self::button or self::a][starts-with(translate(normalize-space(), 'køb', 'KØB'),'KØB')]"
            text = "køb"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[self::button or self::a][starts-with(translate(normalize-space(), 'levering', 'LEVERING'),'LEVERING')]/*")
            x_path = "//*[self::button or self::a][starts-with(translate(normalize-space(), 'levering', 'LEVERING'),'LEVERING')]/*"
            text = "levering"

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath(
                "//*[self::button or self::a][starts-with(translate(normalize-space(), 'levering', 'LEVERING'),'LEVERING')]")
            x_path = "//*[self::button or self::a][starts-with(translate(normalize-space(), 'levering', 'LEVERING'),'LEVERING')]"
            text = "levering"

        return add_to_cart, x_path, text

    def custom_sort(self, url: str) -> bool:
        return url.startswith("/")
    
    def check_products(self, website: str, urls: list) -> bool:
        for url in urls:
            url = url.replace("www.", "")
            if url.startswith("/"):
                url = f"{website}{url}"

            try:
                self.driver.get(url)
            except:
                continue

            sleep(1.2)

            is_valid_page, xpath, text = self.get_cart_btn()

            if is_valid_page:
                try:
                    if is_valid_page.tag_name != "i":
                        t = is_valid_page.text.lower().strip()
                        if t.startswith(text) and self.check_btn_clickable(xpath):
                            return True

                    if self.check_btn_clickable(xpath):
                        return True

                except:
                    ...
            else:
                is_valid_page, xpath = self.get_cart_btn_2()

                if is_valid_page:
                    if self.check_btn_clickable(xpath):
                        return True

            sleep(randrange(2, 4))
        
        return False

    def find_product_on_main_page(self, website: str):
        html = self.driver.page_source
        soup = bs4(html, features="lxml")

        urls = []

        for a_tag in soup.find_all("a", {"href": True}):
            u = a_tag["href"].lower()
            if self.is_valid_url(u, website):
                urls.append(u)

        urls = list(set(urls))
        urls.sort(key=self.custom_sort, reverse=True)
        
        _urls = list(filter(lambda x: x.find("product") != -1 or x.find("produkt") != -1, urls))
        _urls.sort(key=self.custom_sort, reverse=True)
        
        if len(_urls) > 0:
            s = self.check_products(website, _urls)
            if not s:
                self.check_products(website, urls)
        else:
            self.check_products(website, urls)
        

    def check_btn_clickable(self, xpath: str) -> bool:
        return self.driver.find_element(By.XPATH, xpath).is_enabled()

    def handle_sitemap(self, website: str):
        page_src = self.driver.page_source.lower()
        page_src = page_src.replace("&gt;", ">").replace("&lt;", "<")
        
        urls = re.sub('<[^<]+>', " ", page_src)
        urls = re.findall("(?P<url>https?://[^\s]+)", urls)
        urls = list(set(urls))
        
        _urls = []

        for url in urls:
            url = url.replace("www.", "")
            if url.find(website) != -1:
                if url.lower().find(".jpg") != -1 or url.lower().find(".png") != -1 or url.lower().find(".jpeg") != -1 or url.lower().find(".svg") != -1:
                    continue

                if url.lower().find("product") != -1 or url.find("produkt") != -1 or url.find("shop") != -1 or url.lower().find("sitemap") != -1:
                    _urls.append(url)

        for url in _urls:
            if url.lower().find("product") != -1 or url.find("produkt") != -1 or url.find("shop") != -1:
                self.driver.get(url)
                sleep(1.2)
                is_valid_page, xpath, text = self.get_cart_btn()

                if is_valid_page:
                    try:
                        if is_valid_page.tag_name != "i":
                            t = is_valid_page.text.lower().strip()
                            if t.startswith(text) and self.check_btn_clickable(xpath):
                                return

                        if self.check_btn_clickable(xpath):
                            return
                    except:
                        ...
                else:
                    is_valid_page, xpath = self.get_cart_btn_2()

                    if is_valid_page:
                        if self.check_btn_clickable(xpath):
                            return
            elif url.lower().find("sitemap") != -1:
                self.driver.get(url)
                sleep(1.2)
                self.handle_sitemap(website)
                return
            sleep(1.2)

        self.driver.get(website)
        sleep(1.2)
        self.find_product_on_main_page(website)

    def get_product(self, website: str):
        self.driver.get(f"{website}/robots.txt")
        sleep(1.2)

        if self.driver.current_url.find("robots") == -1:
            self.driver.get(f"{website}/sitemap.xml")
            sleep(1.2)
            if self.driver.current_url.find("sitemap") == -1:
                self.driver.get(website)
                sleep(1.2)
                self.find_product_on_main_page(website)
                return

            self.handle_sitemap(website)
            return

        page_src = self.driver.page_source.lower()

        sitemap_1 = page_src.find("sitemap: ")

        if sitemap_1 != -1:
            sitemap_2 = page_src.find("http", sitemap_1)
            sitemap_3 = page_src.find(" ", sitemap_2)
            sitemap_4 = page_src[sitemap_2:sitemap_3]

            sitemap = re.sub('<[^<]+>', "", sitemap_4)
            sitemap = re.search(
                "(?P<url>https?://[^\s]+)", sitemap).group("url")

            _sitemap = urlparse(sitemap)
            _sitemap = _sitemap._replace(netloc=website.replace(
                "https://", "").replace("http://", "").replace("/", ""))

            self.driver.get(_sitemap.geturl())
            sleep(1.2)
            self.handle_sitemap(website)
            return

        self.driver.get(f"{website}/sitemap.xml")
        sleep(1.2)
        if self.driver.current_url.find("sitemap") != -1:
            self.handle_sitemap(website)
        else:
            self.driver.get(website)
            sleep(1.2)
            self.find_product_on_main_page(website)

    def add_product_to_cart(self) -> bool:
        add_to_cart, xpath, text = self.get_cart_btn()

        # print(add_to_cart, xpath)

        if add_to_cart:
            try:
                self.click_using_xpath(xpath=xpath)
            except:
                if xpath.endswith("/*"):
                    xpath = "/*".join(xpath.split("/*")[:2])
                try:
                    self.click_using_xpath(xpath=xpath)
                except:
                    return False
            # self.execute_click_script(add_to_cart)
            sleep(2.3)
            return True
        else:
            add_to_cart, xpath = self.get_cart_btn_2()
            # print(add_to_cart, xpath)
            if add_to_cart:
                try:
                    self.click_using_xpath(xpath=xpath)
                except:
                    if xpath.endswith("/*"):
                        xpath = "/*".join(xpath.split("/*")[:2])
                    try:
                        self.click_using_xpath(xpath=xpath)
                    except:
                        return False
                # self.execute_click_script(add_to_cart)
                sleep(2.3)
                return True

        return False

    def get_checkout_btn(self):
        sleep(2.4)

        btn, x_path = None, None

        btn = self.get_element_by_xpath(
            "//*[starts-with(translate(normalize-space(), 'gå til kassen', 'GÅ TIL KASSEN'),'GÅ TIL KASSEN')]/*")
        x_path = "//*[starts-with(translate(normalize-space(), 'gå til kassen', 'GÅ TIL KASSEN'),'GÅ TIL KASSEN')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til kassen', 'GÅ TIL KASSEN'),'GÅ TIL KASSEN')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til kassen', 'GÅ TIL KASSEN'),'GÅ TIL KASSEN')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til checkout', 'GÅ TIL CHECKOUT'),'GÅ TIL CHECKOUT')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til checkout', 'GÅ TIL CHECKOUT'),'GÅ TIL CHECKOUT')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til checkout', 'GÅ TIL CHECKOUT'),'GÅ TIL CHECKOUT')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til checkout', 'GÅ TIL CHECKOUT'),'GÅ TIL CHECKOUT')]"

        # //*[starts-with(translate(normalize-space(), 'til kassen', 'TIL KASSEN'),'TIL KASSEN')]

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'til kassen', 'TIL KASSEN'),'TIL KASSEN')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'til kassen', 'TIL KASSEN'),'TIL KASSEN')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'til kassen', 'TIL KASSEN'),'TIL KASSEN')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'til kassen', 'TIL KASSEN'),'TIL KASSEN')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'check out', 'CHECK OUT'),'CHECK OUT')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'check out', 'CHECK OUT'),'CHECK OUT')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'check out', 'CHECK OUT'),'CHECK OUT')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'check out', 'CHECK OUT'),'CHECK OUT')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'checkout', 'CHECKOUT'),'CHECKOUT')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'checkout', 'CHECKOUT'),'CHECKOUT')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'checkout', 'CHECKOUT'),'CHECKOUT')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'checkout', 'CHECKOUT'),'CHECKOUT')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'check-out', 'CHECK-OUT'),'CHECK-OUT')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'check-out', 'CHECK-OUT'),'CHECK-OUT')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'check-out', 'CHECK-OUT'),'CHECK-OUT')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'check-out', 'CHECK-OUT'),'CHECK-OUT')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'afslut ordren', 'AFSLUT ORDREN'),'AFSLUT ORDREN')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'afslut ordren', 'AFSLUT ORDREN'),'AFSLUT ORDREN')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'afslut ordren', 'AFSLUT ORDREN'),'AFSLUT ORDREN')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'afslut ordren', 'AFSLUT ORDREN'),'AFSLUT ORDREN')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til bestilling', 'GÅ TIL BESTILLING'),'GÅ TIL BESTILLING')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til bestilling', 'GÅ TIL BESTILLING'),'GÅ TIL BESTILLING')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til bestilling', 'GÅ TIL BESTILLING'),'GÅ TIL BESTILLING')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til bestilling', 'GÅ TIL BESTILLING'),'GÅ TIL BESTILLING')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'bestil', 'BESTIL'),'BESTIL')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'bestil', 'BESTIL'),'BESTIL')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'bestil', 'BESTIL'),'BESTIL')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'bestil', 'BESTIL'),'BESTIL')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'fortsæt til kassen', 'FORTSÆT TIL KASSEN'),'FORTSÆT TIL KASSEN')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'fortsæt til kassen', 'FORTSÆT TIL KASSEN'),'FORTSÆT TIL KASSEN')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'fortsæt til kassen', 'FORTSÆT TIL KASSEN'),'FORTSÆT TIL KASSEN')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'fortsæt til kassen', 'FORTSÆT TIL KASSEN'),'FORTSÆT TIL KASSEN')]"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'videre til levering', 'VIDERE TIL LEVERING'),'VIDERE TIL LEVERING')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'videre til levering', 'VIDERE TIL LEVERING'),'VIDERE TIL LEVERING')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'videre til levering', 'VIDERE TIL LEVERING'),'VIDERE TIL LEVERING')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'videre til levering', 'VIDERE TIL LEVERING'),'VIDERE TIL LEVERING')]"

        if not btn:
            btn = self.get_element_by_xpath(".//*[@name='checkout']")
            x_path = ".//*[@name='checkout']"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til', 'GÅ TIL'),'GÅ TIL')]/*")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til', 'GÅ TIL'),'GÅ TIL')]/*"

        if not btn:
            btn = self.get_element_by_xpath(
                "//*[starts-with(translate(normalize-space(), 'gå til', 'GÅ TIL'),'GÅ TIL')]")
            x_path = "//*[starts-with(translate(normalize-space(), 'gå til', 'GÅ TIL'),'GÅ TIL')]"

        return btn, x_path

    def goto_cart(self, website: str):
        hrefs: 'list[str]' = []
        a_tags = self.driver.find_elements(By.TAG_NAME, "a")

        for tag in a_tags:
            try:
                h = tag.get_attribute("href")
                if not h:
                    continue

                if h.startswith("/"):
                    h = f"{website}{h}"

                hrefs.append(h.lower())
            except:
                ...

        hrefs = list(set(hrefs))

        hrefs = list(filter(lambda x: x.find("cart") != -
                     1 or x.find("kurv") != -1 or x.find("basket") != -1, hrefs))

        sleep(1.2)

        if len(hrefs) == 0:
            return False

        hrefs.sort(key=len)

        for url in hrefs:
            url = urlparse(url)
            path = url.path
            _path = url.path

            if url.path.find("/") != -1:
                path = path.split("/")
                path.pop()
                if path[-1].find("cart") != -1 or path[-1].find("kurv") != -1 or path[-1].find("basket") != -1:
                    _path = "/".join(path)
                else:
                    for i in range(len(path)):
                        p = path[(len(path) - 1) - i]
                        if p.find("cart") != -1 or p.find("kurv") != -1 or p.find("basket") != -1:
                            for x in range(i+1):
                                _path += f"/{path[x]}"
                            break

            _path = re.sub("/{2,}", "/", _path)
            url = f"{url.scheme}://{url.netloc}{_path}"

            self.driver.get(url)
            sleep(1.2)
            if self.get_checkout_btn():
                return True
            else:
                self.driver.get(f"{website}/checkout")
                sleep(1.2)
                return True

        return False

    def accept_terms(self):
        xpaths = [
            ".//*[contains(translate(normalize-space(), 'enig', 'ENIG'), 'ENIG')]/preceding-sibling::input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'enig', 'ENIG'), 'ENIG')]/following-sibling::input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'accept', 'ACCEPT'), 'ACCEPT')]/preceding-sibling::input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'accept', 'ACCEPT'), 'ACCEPT')]/following-sibling::input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'agree', 'AGREE'), 'AGREE')]/preceding-sibling::input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'agree', 'AGREE'), 'AGREE')]/following-sibling::input[@type='checkbox']",

            ".//*[contains(translate(normalize-space(), 'enig', 'ENIG'), 'ENIG')]/preceding-sibling::*/input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'enig', 'ENIG'), 'ENIG')]/following-sibling::*/input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'accept', 'ACCEPT'), 'ACCEPT')]/preceding-sibling::*/input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'accept', 'ACCEPT'), 'ACCEPT')]/following-sibling::*/input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'agree', 'AGREE'), 'AGREE')]/preceding-sibling::*/input[@type='checkbox']",
            ".//*[contains(translate(normalize-space(), 'agree', 'AGREE'), 'AGREE')]/following-sibling::*/input[@type='checkbox']",
        ]

        for x in xpaths:
            e = self.driver.find_elements(By.XPATH, x)

            if e:
                for i in e:
                    self.execute_click_script(i)

    def check_for_payment_gateway_info(self, website: str) -> bool:
        src = self.driver.page_source.lower()

        payment_gateway = None

        for p in self.PAYMENT_GATEWAYS:
            p = p.lower()
            if src.find(p) != -1:
                payment_gateway = p
                break
            elif src.find(p.replace(" ", "_")) != -1:
                payment_gateway = p
                break

        if payment_gateway:
            if payment_gateway == "payments.nets":
                payment_gateway = "nets"

            self.save_to_output(website, payment_gateway)
            return True

        return False

    def do_checkout(self, website: str):
        sleep(2.4)

        btn, xpath = self.get_checkout_btn()

        try:
            self.accept_terms()
            self.click_using_xpath(xpath)
            sleep(1.2)
        except:
            ...

        success = self.check_for_payment_gateway_info(website)

        if not success:
            print(f"{website}: Not found!")

    def close_dialogs(self):
        dialog = self.get_element_by_xpath(
            ".//*[@role='dialog']//*[@type='submit']")

        if dialog:
            self.click_using_xpath(".//*[@role='dialog']//*[@type='submit']")

        sleep(3.6)

    @staticmethod
    def clean_url(url: str) -> str:
        url = url.replace("www.", "").replace("ww.", "").replace(
            "https://", "").replace("http://", "")

        if url.endswith("/"):
            url = url.removesuffix("/")

        return url

    def start_main_process(self):
        websites = list(map(model.clean_url, model.WEBSITES))

        for website in websites:
            website = f'https://{website.replace("www.", "")}'
            print(f"Current Website: {website}")

            try:
                self.driver.get(website)
            except:
                print(f"Website could not be loaded: {website}")
                continue

            sleep(3.7)

            self.close_dialogs()
            self.get_product(website=website)

            added = self.add_product_to_cart()
            sleep(2.6)
            if added:
                success = self.goto_cart(website=website)
                if success:
                    self.do_checkout(website)

            print(f"Finished: {website}")
            sleep(4000.5)

        print("All finished!")

    def main(self):
        self.init_webdriver()
        sleep(1.3)
        self.start_main_process()
        sleep(3.2)
        self.driver.quit()


if __name__ == "__main__":
    model = PaymentProviderFetcher()
    model.main()

# -----------------
# givingdeer.dk
# fitnesscoaching.dk
# danishendurance.com
# Bygmax.dk
# brand-art.dk
# annavonlipa.com
# Klub-modul.dk
# enamelcopenhagen.dk
# nordbrands.dk
# nyesokker.dk
# elysiumbyam.com
# merkdesignstudio.dk
# natruba.dk
# zizzi.dk
# skatepro.dk
# liberte.dk
# vinylpladen.dk
# -----------------
# xl-byg.dk
# matas.dk
# apopro.dk
# coolshop.dk
# silvan.dk
# sostrenegrene.com
# bygma.dk
# power.dk
# elgiganten.dk
# nicehair.dk
# beautycos.dk
# kop-kande.dk
# imerco.dk
# maxizoo.dk
# nemlig.com
# -----------------
