import json
import pickle
from os import path
from time import sleep

from chromedriver_py import binary_path  # this will get you the path variable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from notifications.notifications import NotificationHandler
from utils import selenium_utils
from utils.logger import log
from utils.selenium_utils import options, enable_headless

LOGIN_URL = "https://account.asus.com/loginform.aspx?skey=d39ad7681c9643d5a194d25bc71800fa"
CONFIG_PATH = "asus_config.json"


#def is_loaded(d):
#    page_state = d.execute_script('return document.readyState;')
#    return page_state == "complete"
def wait_until_loaded(d, timeout=20):
    log.info("Waiting for page to load at {}.".format(d.driver.current_url))
    old_page = d.find_element_by_tag_name('html')
    yield
    WebDriverWait(d, timeout).until(staleness_of(old_page))

class Evga:
    def __init__(self, headless=False):
        if headless:
            enable_headless()
        self.driver = webdriver.Chrome(executable_path=binary_path, options=options)
        self.credit_card = {}
        self.card_pn = ""
        self.card_series = ""
        self.notification_handler = NotificationHandler()

        try:
            if path.exists(CONFIG_PATH):
                with open(CONFIG_PATH) as json_file:
                    config = json.load(json_file)
                    username = config["username"]
                    password = config["password"]
                    self.card_pn = config.get("card_pn")
                    self.card_series = config["card_series"]
                    self.credit_card["name"] = config["credit_card"]["name"]
                    self.credit_card["number"] = config["credit_card"]["number"]
                    self.credit_card["cvv"] = config["credit_card"]["cvv"]
                    self.credit_card["expiration_month"] = config["credit_card"][
                        "expiration_month"
                    ]
                    self.credit_card["expiration_year"] = config["credit_card"][
                        "expiration_year"
                    ]
        except Exception as e:
            log.error(f"This is most likely an error with your {CONFIG_PATH} file.")
            raise e

        self.login(username, password)

    def login(self, username, password):
        """
        We're just going to attempt to load cookies, else enter the user info and let the user handle the captcha
        :param username:
        :param password:
        :return:
        """
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36"
            },
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        if path.isfile("asus-cookies.pkl"):  # check for cookies file
            self.driver.get("https://www.asus.com")
            selenium_utils.wait_for_page(
                self.driver, "ASUS USA", 300
            )
            cookies = pickle.load(open("asus-cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)

        self.driver.get("https://store.asus.com/us")
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div/header/div[1]/nav[2]/ul/li[3]/div')
            )
        ).click()
        if (
            len(self.driver.find_elements_by_id("login_link")) > 0
        ):  # cookies did not provide logged in state
            self.driver.get(LOGIN_URL)
            selenium_utils.wait_for_page(self.driver, "Asus Account")

            selenium_utils.field_send_keys(self.driver, '//*[@id="Front_txtAccountID"]', username)
            selenium_utils.field_send_keys(self.driver, '//*[@id="Front_txtPassword"]', password)

            log.info("Go do the captcha and log in")

            selenium_utils.wait_for_page(
                self.driver, "My Profile", 300
            )
            pickle.dump(
                self.driver.get_cookies(), open("asus-cookies.pkl", "wb")
            )  # save cookies

        log.info("Logged in!")
    def buy(self, delay=25, test=False):
#        if test:
#            log.info("Refreshing Page Until Title Matches ...")
#            selenium_utils.wait_for_title(
#                self.driver,
#                "EVGA - Products - Graphics - GeForce 16 Series Family - GTX 1660",
#                "https://www.evga.com/products/ProductList.aspx?type=0&family=GeForce+16+Series+Family&chipset=GTX+1660",
#            )
#        else:
#            log.info("Refreshing Page Until Title Matches ...")
#            selenium_utils.wait_for_title(
#                self.driver,
#                "EVGA - Products - Graphics - GeForce 30 Series Family - RTX "
#                + self.card_series,
#                "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+30+Series+Family&chipset=RTX+"
#                + self.card_series,
#            )
#
#        log.info("matched chipset=RTX+" + self.card_series + "!")
#
#        if self.card_pn and not test:
#            # check for card
#            log.info("On GPU list Page")
#            card_btn = self.driver.find_elements_by_xpath(
#                "//a[@href='/products/product.aspx?pn=" + self.card_pn + "']"
#            )
#            while not card_btn:
#                log.debug("Refreshing page for GPU")
#                self.driver.refresh()
#                card_btn = self.driver.find_elements_by_xpath(
#                    "//a[@href='/products/product.aspx?pn=" + self.card_pn + "']"
#                )
#                sleep(delay)
#
#            card_btn[0].click()
        self.driver.get("https://store.asus.com/us/item/202009AM290000002/ASUS-ROG-STRIX-NVIDIA-GeForce-RTX-3080-OC-Edition-Gaming-Graphics-Card-%28PCIe-4.0%2C-10GB-GDDR6X%2C-HDMI-2.1%2C-DisplayPort-1.4a%2C-Axial-tech-Fan-Design%2C-2.9-slot%2C-Super-Alloy-Power-II%2C-GPU-Tweak-II%29")
        #  Check for stock
        log.info("On GPU Page")
        first = True
        while True:
            atc_buttons = False
            while not atc_buttons:
                if not first:
                    sleep(15)
                    log.debug("Refreshing page for GPU")
                    self.driver.refresh()
                else:
                    first = False
#             wait_until_loaded(self.driver)
                sleep(10)
                atc_buttons = self.driver.find_element_by_xpath(
                    '//*[@id="item_add_cart"]'
                )

            try:
                log.info("click add to cart")
                #  Add to cart
                atc_buttons.click()
                break
            except:
                continue

        log.info("send notification")
        # Send notification that product is available
        self.notification_handler.send_notification(
            f"📦 Card found in stock at ASUS"
        )

        log.info("waiting for checkout page")
        #  Go to checkout
        selenium_utils.wait_for_page(self.driver, "Welcome to ASUS Online Store - ASUS Store", 300)
#        selenium_utils.button_click_using_xpath(
#            self.driver, '//*[@id="LFrame_CheckoutButton"]'
#        )
#
#        # Shipping Address screen
#        selenium_utils.wait_for_page(self.driver, "Shopping")

        log.info("Skip that page.")
        self.driver.get("https://shop-us1.asus.com/AW000706/checkout")

        selenium_utils.wait_for_page(self.driver, "Checkout - ASUS Store")

        log.info("Ensure that we are paying with credit card")
#        sleep(3)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout-step__shipping-and-billing"]/div[4]/div/a'))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="form-shipping-method"]/div/div/div[3]/div/label')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="checkout-step__shipping-method"]/div[2]/div/a')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="form-customer-info"]/div/div/div[1]/div/div/label')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="continueBtn"]')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="checkout-step__review"]/div[2]/div[4]/div[2]/div/div[1]/label')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="checkout-step__review"]/div[2]/div[4]/div[2]/div/div[2]/label')
            )
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="checkout-step__review"]/div[2]/div[4]/div[3]/a')
            )
        ).click()

        selenium_utils.wait_for_page(self.driver, "Payment Acceptance", 300)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="card_type_001"]')
            )
        ).click()
        selenium_utils.wait_for_element(self.driver, "ctl00_LFrame_txtNameOnCard")

        log.info("Populate credit card fields")

#        selenium_utils.field_send_keys(
#            self.driver, "ctl00$LFrame$txtNameOnCard", self.credit_card["name"]
#        )
        selenium_utils.field_send_keys(
            self.driver, '//*[@id="card_number"]', self.credit_card["number"]
        )
        sel = selenium.webdriver.support.ui.Select(self.driver.find_element_by_xpath('//*[@id="card_expiry_month"]'))
        sel.select_by_visible_text(self.credit_card["expiration_month"])
        sel = selenium.webdriver.support.ui.Select(self.driver.find_element_by_xpath('//*[@id="card_expiry_year"]'))
        sel.select_by_visible_text(self.credit_card["expiration_year"])

        selenium_utils.field_send_keys(
            self.driver, '//*[@id="card_cvn"]', self.credit_card["cvv"]
        )


        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="payment_details_lower"]/input[2]')
                )
            ).click()
        except:
            pass

        log.info("Finalize Order Page")
#        selenium_utils.wait_for_page(self.driver, "EVGA - Checkout - Finalize Order")
#
#        WebDriverWait(self.driver, 10).until(
#            EC.element_to_be_clickable((By.ID, "ctl00_LFrame_cbAgree"))
#        ).click()
#
#        if not test:
#            WebDriverWait(self.driver, 10).until(
#                EC.element_to_be_clickable((By.ID, "ctl00_LFrame_btncontinue"))
#            ).click()

        log.info("Finalized Order!")

        # Send extra notification alerting user that we've successfully ordered.
        self.notification_handler.send_notification(
            f"🎉 Order submitted at EVGA for {self.card_pn}",
            audio_file="purchase.mp3",
        )
