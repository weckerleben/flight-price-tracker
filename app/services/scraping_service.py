import logging as log

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.config import SEARCH_SLEEP_SEC
from app.utils.logger import configure_log
from app.utils.utils import countdown_timer

configure_log()


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
        countdown_timer(SEARCH_SLEEP_SEC)
        current_url = driver.current_url
        if current_url != URL:
            log.warning(f"The current URL {current_url} does not match the expected {URL}.")
            return 9999, "URL mismatch"
        recommended_price_element = driver.find_element(By.CSS_SELECTOR, '[data-content="price_a"]')
        recommended_price = recommended_price_element.text.replace('Cheapest', '').replace('\n', '')
        price = recommended_price.split(' • ')[0].replace('$', '').replace(',', '') if recommended_price else "9999"
        duration = recommended_price.split(' • ')[1].replace('h ', ':').replace('m',
                                                                                '') if recommended_price else "00:00"
        return price, duration
    except TimeoutException:
        log.info("Timeout occurred while waiting for elements to disappear or locating the price.")
        return 9999, "00:00"
    except NoSuchElementException:
        log.info(f"No flights were found for {URL[38:48]} to {URL[49:59]}")
        return 9999, "00:00"
