import logging
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.logger import configure_logging

configure_logging()


def wait_for_at_least_n_elements_and_no_captcha(driver, css_selector, n, timeout=10):
    class CombinedCondition:
        """Define a combined condition for WebDriverWait."""

        def __call__(self, driver):
            elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
            captcha_present = len(driver.find_elements(By.CSS_SELECTOR, ".WZTU-captcha")) > 0
            logging.critical(captcha_present)
            return len(elements) >= n and not captcha_present

    WebDriverWait(driver, timeout).until(CombinedCondition())


def scrape_best_price(driver, URL):
    try:
        driver.get(URL)
        time.sleep(10)  # Considerar ajustar o eliminar este sleep si no es necesario
        wait_for_at_least_n_elements_and_no_captcha(driver, ".nrc6", 1, timeout=10)
        recommended_price_element = driver.find_element(By.CSS_SELECTOR, '[data-content="price_a"]')
        recommended_price = recommended_price_element.text.replace('Cheapest', '').replace('\n', '')
        price = recommended_price.split(' • ')[0].replace('$', '').replace(',', '') if recommended_price else ""
        duration = recommended_price.split(' • ')[1].replace('h ', ':').replace('m', '') if recommended_price else ""
        return price, duration
    except TimeoutException:
        return 0, "00:00"
