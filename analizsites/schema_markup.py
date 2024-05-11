from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.webdriver import Chrome

from sitemain.settings import logger

from .captcha import GoogleRecaptcha
from .common import CommonMethod


class SchemaMarkup:

    """ Получение микроразметки schema.org """

    @classmethod
    def get_schema_markup(cls, url: str, schema_bool: bool = True, site_save: bool = True) -> dict | str:
        if not schema_bool:
            logger.info('Микроразметку Schema.org не проверяем, пришёл параметр.')
            return {'schema': 'jsfunc'}

        validate_url = 'https://validator.schema.org/'

        for i in range(1, 3):
            schema_res = cls.get_schema_markup_driver(validate_url, url, i)
            if schema_res: break

        if not schema_res: schema_res = 'не получено'
        if site_save:
            return {'schema': schema_res}
        else: return schema_res

    @classmethod
    def get_schema_markup_driver(cls, validate_url: str, url: str, j: int) -> Optional[str]:
        driver, schema_res = None, None
        try:
            driver = CommonMethod.get_start_driver(url=validate_url, headless=True, browser=None, size=None, fonts=True)

            schema_res = cls.get_schema_result_input_txt(driver, url)
            if schema_res:
                logger.info(f'{validate_url} - Микроразметка получена без капчи. Номер цикла - {j}')

            elif schema_res is False:
                logger.error('schema_markup - Капча. Нужно разгадывать. ')

                count_steps = GoogleRecaptcha.solving_recaptcha(driver)

                # verification captcha
                schema_res = cls.get_schema_result_input_txt(driver, url)
                if schema_res:
                    logger.info(f'{validate_url}  - микроразметка  получена с помощью капчи. Номер цикла - {j}. Кол-во попыток - {count_steps}')

        except Exception as e:
            logger.error(f'{type(e)}\n{e}')
        finally:
            if driver: driver.quit()

        return schema_res

    @classmethod
    def get_schema_result_input_txt(cls, driver: Chrome, url: str) -> str | bool | None:
        captcha_form = driver.find_elements(By.ID, 'captcha-form')
        if captcha_form:
            return False
        try:
            input_url = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#new-test-url-input')))
            input_url.send_keys(url)
            button_send = driver.find_element(By.CSS_SELECTOR, 'button#new-test-submit-button')
            button_send.click()
            # wait result
            try:
                schema_block = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sKfxWe-BeDmAc.sKfxWe-BeDmAc-AHe6Kc')))
                schema_text = schema_block.text
                if schema_text == 'Ничего не обнаружено':
                    schema_res = 'не найдена'
                else: schema_res = 'найдена'
                return schema_res
            except Exception as e:
                logger.error(f'schema_markup - {type(e)}\n{e}')
        except Exception as e:
            logger.error(f'{type(e)} - {e}')

        return None
