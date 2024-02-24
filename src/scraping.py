import logging
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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


def wait_for_element_absence(driver, css_selector, timeout=86400):
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def initial_scrape_conf(driver, URL):
    driver.get(URL)
    wait_for_element_absence(driver, ".biRz-loading")
    wait_for_element_absence(driver, ".WZTU")
    wait_for_element_absence(driver, ".biRz-loading")
    wait_for_element_absence(driver, ".WZTU")


def scrape_best_price(driver, URL):
    try:
        driver.get(URL)
        wait_for_element_absence(driver, ".biRz-loading")
        wait_for_element_absence(driver, ".WZTU")
        wait_for_element_absence(driver, ".biRz-loading")
        wait_for_element_absence(driver, ".WZTU")
        current_url = driver.current_url
        if current_url != URL:
            logging.warning(f"The current URL {current_url} does not match the expected {URL}.")
            return 9999, "URL mismatch"
        recommended_price_element = driver.find_element(By.CSS_SELECTOR, '[data-content="price_a"]')
        recommended_price = recommended_price_element.text.replace('Cheapest', '').replace('\n', '')
        price = recommended_price.split(' • ')[0].replace('$', '').replace(',', '') if recommended_price else ""
        duration = recommended_price.split(' • ')[1].replace('h ', ':').replace('m', '') if recommended_price else ""
        return price, duration
    except TimeoutException:
        logging.info("Timeout occurred while waiting for elements to disappear or locating the price.")
        return 99999, "00:00"
    except NoSuchElementException:
        logging.info(f"No flights were found for {URL[38:48]} to {URL[49:59]}")
        return 99999, "00:00"
