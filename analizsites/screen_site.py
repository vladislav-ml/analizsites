import os
from datetime import datetime

from sitemain.settings import logger

from .common import CommonMethod


class ScreenSite:

    """ Скриншот сайта """

    @classmethod
    def get_screenshot_site(cls, url: str, create_time: datetime, screen_bool: bool) -> dict:
        if not screen_bool:
            logger.info(f'{url} - Скриншот не делаем. Пришел параметр.')
            return {}
        driver, img_src = None, None
        domen = CommonMethod.get_domen(url)
        create_year = str(create_time.year)
        create_month = str(create_time.month)
        create_day = str(create_time.day)

        os.makedirs(os.path.join(os.getcwd(), 'media', 'sites', create_year, create_month, create_day), exist_ok=True)
        full_path_img = os.path.join(os.getcwd(), 'media', 'sites', create_year, create_month, create_day, f'{domen}.png')

        try:
            driver = CommonMethod.get_start_driver(url=url, headless=True, browser='Mozilla/5.0 (Android 12; Mobile; LG-M255; rv:101.0) Gecko/101.0 Firefox/101.0', size=True, fonts=False)

            driver.save_screenshot(full_path_img)
            logger.info(f'{domen} - Скриншот сделан.')
            img_src = os.path.join(os.sep, 'media', 'sites', create_year, create_month, create_day, f'{domen}.png')

        except Exception as e:
            logger.error(f'{domen} - не удалось сделать скриншот страницы - {type(e)}\n{e}')
        finally:
            if driver: driver.quit()
            return {'img': img_src}
