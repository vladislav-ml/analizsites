import re

from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.webdriver import Chrome

from sitemain.settings import logger

from .captcha import GoogleRecaptcha
from .common import CommonMethod


class GooglePages:

    """ Получение кол-ва сраниц сайта в google """

    @classmethod
    def get_google_pages(cls, url: str) -> dict:
        domen = CommonMethod.get_domen(url)
        current_url = f'https://www.google.com/search?q=site%3A{domen}'
        resp = CommonMethod.send_response(current_url)
        if not resp:
            logger.error(f'Ошибка в запросе - {current_url}')
            return {}
        soup = BS(resp.content.decode('utf-8'), 'html.parser')

        # есть кол-во страниц
        google_pages = cls.get_google_count(soup=soup)
        if google_pages:
            logger.info(f'{current_url}  - Значение получено с помощью requests')
        if not google_pages:
            for i in range(1, 4):
                google_pages = cls.get_google_pages_driver(current_url, domen, i)
                if google_pages:
                    break

        if not google_pages: google_pages = 'не удалось получить'
        return {'google_pages': google_pages}

    @classmethod
    def get_google_pages_driver(cls, current_url: str, domen: str, i: int) -> str | bool | None:
        google_pages = None
        try:
            driver = CommonMethod.get_start_driver(url=current_url, headless=True, browser=None, size=None, fonts=True)
            google_pages = cls.get_google_count(driver=driver, type_requests=2)
            if google_pages:
                logger.info(f'{current_url}  - Значение получено с помощью driver. Кол-во попыток - {i}')
            if google_pages is False:
                logger.warning(f'{current_url} - капча. Нужно разгадывать.')
                count_steps = GoogleRecaptcha.solving_recaptcha(driver)
                google_pages = cls.get_google_count(driver=driver, type_requests=2)
                if google_pages:
                    logger.info(f'{current_url}  - Значение получено с помощью капчи. Номер цикла - {i}. Кол-во попыток - {count_steps}')

        except Exception as e:
            logger.error(f'{type(e)}\n{e}')
        finally:
            if driver: driver.quit()
        return google_pages

    @classmethod
    def get_google_count(cls, soup: BS = None, driver: Chrome = None, type_requests: int = 1) -> str | bool | None:
        result = None
        if driver:
            captcha_form = driver.find_elements(By.CSS_SELECTOR, '#captcha-form')
            if captcha_form:
                return False
        if type_requests == 2:
            try:
                WebDriverWait(driver, 5).until(lambda driver: driver.find_elements(By.ID, 'result-stats') or driver.find_elements(By.CLASS_NAME, 'card-section') or driver.find_elements(By.CSS_SELECTOR, 'div.BNeawe.tAd8D.AP7Wnd'))
                soup = BS(driver.page_source, 'html.parser')
            except:
                return None
        block_res = soup.find_all('div', attrs={'id': 'result-stats'})
        block_no_found = soup.find_all('div', attrs={'class': 'card-section'})
        block_no_found_no_section = soup.select('div.BNeawe.tAd8D.AP7Wnd')
        if block_res:
            str_res = block_res[0].text
            arr_res = re.findall(r'([0-9\s]+)[-\(]+', str_res)
            result = arr_res[0].strip() if arr_res else None
        elif block_no_found:
            result = '0'
        elif block_no_found_no_section:
            block_txt = block_no_found_no_section[0].text
            if 'ничего не найдено' in block_txt:
                result = '0'

        return result
