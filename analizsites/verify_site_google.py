from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sitemain.settings import logger

from .captcha import GoogleRecaptcha
from .common import CommonMethod


class VerifyGoogle:

    """ Безопасность сайта в google """

    @classmethod
    def verify_site_google(cls, url):
        verify = False
        for i in range(1, 4):
            verify = cls.verify_site_google_driver(url, i)
            if verify: break

        if not verify: verify = 'не получено'
        return {'verify': verify.lower()}

    @classmethod
    def found_block_verify(cls, driver):
        captcha_form = driver.find_elements(By.ID, 'captcha-form')
        if captcha_form:
            return False
        try:
            verify = 'не определено'
            span_block = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label="figure value"]')))
            if span_block:
                if 'Не найдено небезопасного контента.' in span_block.text:
                    verify = 'Cайт безопасен'
                else: verify = span_block.text
            return verify
        except Exception as e:
            logger.error(f'found_block_verify - {type(e)}\n{e}')
        return None

    @classmethod
    def verify_site_google_driver(cls, url, i):
        verify, driver = None, None
        domen = CommonMethod.get_domen(url)
        validate_url = f'https://transparencyreport.google.com/safe-browsing/search?url={domen}&hl=ru'

        try:
            driver = CommonMethod.get_start_driver(url=validate_url, headless=True, browser=None, size=None, fonts=True)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label="figure value"]')))
            except: pass

            verify = cls.found_block_verify(driver)
            if verify:
                logger.info(f'Значение безопасности сайта получено без капчи, но с driver! Кол-во попыток - {i}.')
            elif verify is False:
                logger.error('verify - Капча. Нужно разгадывать. ')

                count_steps = GoogleRecaptcha.solving_recaptcha(driver)

                # verification captcha
                verify = cls.found_block_verify(driver)
                if verify:
                    logger.info(f'{validate_url}  - безопасность от google  получена с помощью капчи. Номер цикла - {i}. Кол-во попыток - {count_steps}')

        except Exception as e:
            logger.error(f'{type(e)} - {e}')
        finally:
            if driver: driver.quit()
        return verify
