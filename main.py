import re

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import selenium.webdriver.support.expected_conditions as EC
import undetected_chromedriver as uc

from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
from random import randrange
from time import sleep


class PaymentProviderFetcher():
    def __init__(self):
        # open("payment_gateways.txt", encoding="utf8").read().strip().lower().split('\n')
        self.PAYMENT_GATEWAYS = ["Pensopay", "Clearhaus", "Quickpay", "Bambora", "Worldline", "Reepay", "Valitor", "Freepay", "Adyen",
                                 "Farpay", "Lunar", "Nets", "Stripe", "Shipmondo Payments", "Shopify payments", "Onpay", "Elevon", "Swiipe", "Paylike"]
        self.WEBSITES = open("urls.txt", encoding="utf8").read(
        ).strip().lower().replace("\r", "").split("\n")

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

    def is_valid_url(self, url, website) -> bool:
        if self.driver.current_url.find(url) != -1:
            return False

        if url == f"{website.lower()}/" or url == website.lower():
            return False

        if not url.startswith("/"):
            if url.find(website.lower()) == -1:
                return False

        if url.find("/blog") != -1 or url.find("/kontakt") != -1 or url.find("/contact") != -1 or url.find("/about") != -1 or url.find("/om") != -1 or url.find("/faq") != -1 or url.find("/login") != -1 or url.find("/konto") != -1 or url.find("/account") != -1 or url.find("/create") != -1 or url.find("/sign") != -1:
            return False

        return True

    def get_element_by_xpath(self, xpath: str):
        return self.driver.execute_script(f"return document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue")

    def execute_click_script(self, elem):
        self.driver.execute_script("arguments[0].click()", elem)

    def get_cart_btn(self) -> 'WebElement | None':
        add_to_cart = None

        add_to_cart = self.get_element_by_xpath("//*[text()='Tilføj til kurv']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Læg i kurv']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Add to cart']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Add to basket']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Tilføj til indkøbskurv']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Føj til kurv']")

        if not add_to_cart:
            add_to_cart = self.get_element_by_xpath("//*[text()='Køb']")

        return add_to_cart

    def find_product_on_main_page(self, website: str):
        html = self.driver.page_source
        soup = bs4(html, features="lxml")

        urls = []

        for a_tag in soup.find_all("a", {"href": True}):
            urls.append(a_tag["href"].lower())

        urls.sort(key=len, reverse=False)

        for url in urls:
            if not self.is_valid_url(url, website):
                continue

            # if url.find("product") != -1 or url.find("produkt") != -1 or url.find("categor") != -1 or url.find("kategori") != -1:
            #     if url.startswith("/"):
            #         url = f"{website}{url}"

            #     self.driver.get(url)

            #     if self.get_cart_btn():
            #         return

            #     self.find_product_on_main_page(website)
            # else:

            # for _ in range(self.page_deepness):
            if url.startswith("/"):
                url = f"{website}{url}"

            try:
                self.driver.get(url)
            except:
                continue

            if self.get_cart_btn():
                return          

    def handle_sitemap(self, website: str):
        page_src = self.driver.page_source.lower()
        urls = re.sub('<[^<]+>', "", page_src)
        urls = re.findall("(?P<url>https?://[^\s]+)", urls)

        for url in urls:
            if url.find(website) != -1:
                if url.lower().find(".jpg") != -1 or url.lower().find(".png") != -1 or url.lower().find(".jpeg") != -1 or url.lower().find(".svg") != -1:
                    continue

                if url.lower().find("product") != -1 or url.find("produkt") != -1:
                    self.driver.get(url)
                    if url.lower().find("sitemap") != -1:
                        self.handle_sitemap(website)
                        return
                    else:
                        return

                elif url.lower().find("sitemap") != -1:
                    self.driver.get(url)
                    self.handle_sitemap(website)
                    return

        # l_url = max(urls, key=len)
        # self.driver.get(url)

        self.driver.get(website)
        self.find_product_on_main_page(website)

    def get_product(self, website: str):
        self.driver.get(f"{website}/robots.txt")

        if self.driver.current_url.find("robots") == -1:
            self.driver.get(f"{website}/sitemap.xml")

            if self.driver.current_url.find("sitemap") == -1:
                self.driver.get(website)
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

        self.driver.get(f"{website}/sitemap.xml")

        if self.driver.current_url.find("sitemap") != -1:
            self.handle_sitemap(website)
        else:
            self.driver.get(website)
            self.find_product_on_main_page(website)

    def add_product_to_cart(self) -> bool:
        add_to_cart = self.get_cart_btn()

        if add_to_cart:
            self.execute_click_script(add_to_cart)
            sleep(1.3)
            return True

        return False

    def get_checkout_btn(self) -> 'WebElement | None':
        sleep(2.4)

        try:
            btn = self.driver.find_element(
                By.XPATH, "//*[contains(translate(text(), 'kassen', 'KASSEN'),'KASSEN')]")
        except:
            try:
                btn = self.driver.find_element(
                    By.XPATH, "//*[contains(translate(text(), 'bestilling', 'BESTILLING'),'BESTILLING')]")
            except:
                try:
                    btn = self.driver.find_element(
                        By.XPATH, "//*[contains(translate(text(), 'ordren', 'ORDREN'),'ORDREN')]")
                except:
                    try:
                        btn = self.driver.find_element(
                            By.XPATH, "//*[contains(translate(text(), 'check out', 'CHECK OUT'),'CHECK OUT')]")
                    except:
                        try:
                            btn = self.driver.find_element(
                                By.XPATH, "//*[contains(translate(text(), 'checkout', 'CHECKOUT'),'CHECKOUT')]")
                        except:
                            try:
                                btn = self.driver.find_element(
                                    By.CSS_SELECTOR, "*[name=checkout]")
                            except:
                                btn = None

        return btn

    def goto_cart(self, website: str):
        hrefs: 'list[str]' = []
        a_tags = self.driver.find_elements(By.TAG_NAME, "a")

        for tag in a_tags:
            try:
                h = tag.get_attribute("href")
                if h.startswith("/"):
                    h = f"{website}{h}"
                hrefs.append(h)
            except:
                ...

        hrefs = list(set(hrefs))
        hrefs = list(filter(lambda x: x.find("/cart") != -1, hrefs))

        if len(hrefs) == 0:
            hrefs = list(filter(lambda x: x.find("/kurv") != -1, hrefs))

        for url in hrefs:
            url = urlparse(url)
            path = url.path
            _path = url.path

            if url.path.find("/") != -1:
                path = path.split("/")
                path.pop()
                if path[-1].find("cart") != -1:
                    _path = "/".join(path)
                else:
                    for i in range(len(path)):
                        p = path[(len(path) - 1) - i]
                        if p.find("cart") != -1 or p.find("kurv") != -1:
                            for x in range(i+1):
                                _path += f"/{path[x]}"
                            break

            _path = re.sub("/{2,}", "/", _path)
            url = f"{url.scheme}://{url.netloc}{_path}"

            self.driver.get(url)

            if self.get_checkout_btn():
                return True

        return False

    def do_checkout(self):
        btn = self.get_checkout_btn()

        try:
            btn.click()
        except:
            try:
                self.execute_click_script(btn)
            except Exception as e:
                print(e)
                return

    def start_main_process(self):
        for website in self.WEBSITES:
            website = f"https://{website}"
            print(f"Current Website: {website}")

            try:
                self.driver.get(website)
            except:
                print(f"Website could not be loaded: {website}")
                sleep(1.2)
                continue

            sleep(6.7)

            self.get_product(website=website)

            added = self.add_product_to_cart()
            # sleep(2.6)
            if added:
                success = self.goto_cart(website=website)
                if success:
                    self.do_checkout()
            print("Finished!")
            sleep(4000.5)

    def main(self):
        self.init_webdriver()
        sleep(1.3)
        self.start_main_process()
        sleep(3.2)
        self.driver.quit()


if __name__ == "__main__":
    model = PaymentProviderFetcher()
    model.main()
    
    # model.init_webdriver()
    # sleep(1.3)
    # # model.get_checkout_btn("https://www.skatepro.dk/catalog/cart.php")
    # # model.get_checkout_btn("https://www.sortesokker.dk/checkout/cart/")
    # model.get_checkout_btn("https://enamelcopenhagen.dk/cart")
    # model.get_checkout_btn("https://www.natruba.dk/cart")

    # urls = re.sub('<[^<]+>', "", "<loc>https://danishendurance.com/products/compression-socks</loc> <lastmod>2023-03-14T12:03:13+01:00</lastmod> <changefreq>daily</changefreq> <image:image> <image:loc>https://cdn.shopify.com/s/files/1/0357/2999/7883/products/compression-socks-396890.jpg?v=1664873853</image:loc> <image:title>COMPRESSION SOCKS</image:title> <url> <loc>https://danishendurance.com/products/organic-cotton-compression-socks</loc> <lastmod>2023-03-14T14:44:21+01:00</lastmod>")
    # urls = re.findall("(?P<url>https?://[^\s]+)", urls)
    # print(urls)
    # model.execute_click_xpath("//*[text()='Tilføj til kurv']", "https://danishendurance.com/products/compression-socks")

    # l = ["https://www.skatepro.dk/catalog/cart.php",
    #      "https://www.sortesokker.dk/checkout/cart/",
    #      "https://enamelcopenhagen.dk/cart",
    #      "https://www.natruba.dk/cart"]
    # l.sort(key=len, reverse=True)
    # print(l)
