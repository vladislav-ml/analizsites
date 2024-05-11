import os
import random
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import requests
from dotenv import dotenv_values
from selenium import webdriver as webdriver_main
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from sitemain.settings import logger

config = dotenv_values('.env')
RUCAPTCHA_KEY = config['RUCAPTCHA_KEY']


class CommonMethod:

    errors = {
        'ERROR_WRONG_USER_KEY': 'Вы указали значение параметра key в неверном формате, ключ должен содержать 32 символа.',
        'ERROR_KEY_DOES_NOT_EXIST': 'Ключ, который вы указали, не существует. ',
        'ERROR_ZERO_BALANCE': 'На вашем счету недостаточно средств.',
        'ERROR_PAGEURL': 'Параметр pageurl не задан в запросе.',
        'ERROR_NO_SLOT_AVAILABLE': 'Очередь ваших капч, которые ещё не распределены на работников, слишком длинная.',
        'IP_BANNED': 'Ваш IP-адрес заблокирован за чрезмерное количество попыток авторизации с неверным ключем авторизации.	Бан будет автоматически снят через 5 минут.',
        'ERROR_BAD_TOKEN_OR_PAGEURL': 'Невалидная пара значений googlekey и pageurl.',
        'ERROR_GOOGLEKEY': 'Параметр sitekey в запросе пустой или имеет некорректный формат.',
        'ERROR_PROXY_FORMAT': 'Некорректный формат прокси при отправке запроса',
        'ERROR_WRONG_GOOGLEKEY': 'Параметр googlekey отсутствует в вашем запросе.',
        'ERROR_CAPTCHAIMAGE_BLOCKED': 'Изображение, которые помечено в нашей базе данных как нераспознаваемое.',
        'TOO_MANY_BAD_IMAGES': 'Вы присылаете слишком много изображений, которые невозможно распознать',
        'MAX_USER_TURN': 'Больше 60 обращений в течение 3 секунд.',
        'ERROR_BAD_PARAMETERS': 'В запросе отсутствуют обязательные параметры или значения параметров имеют некорректный формат.',
        'ERROR_BAD_PROXY': 'Прокси-сервер был помечен ПЛОХИМ',
        'ERROR_WRONG_ID_FORMAT': 'ID капчи в неправильном формате.',
        'ERROR_WRONG_CAPTCHA_ID': 'Отправлен неверный ID капчи.',
        'ERROR_EMPTY_ACTION': 'Параметр action не был передан или передан без значения.',
        'ERROR_PROXY_CONNECTION_FAILED': 'Не удалось загрузить капчу через ваш прокси-сервер.'
    }

    @classmethod
    def get_domen(cls, url: str) -> str:
        return urlparse(url).hostname

    @classmethod
    def get_random_item(cls, file: str) -> str:
        current_path = os.path.join(os.getcwd(), 'info', file)
        with open(current_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line and line != '\n' and not line.startswith('#')]
        if lines:
            return random.choice(lines)
        return ''

    @classmethod
    def interceptor(cls, request) -> None:
        referer = cls.get_random_item('referer.txt')
        del request.headers['Referer']
        request.headers['Referer'] = referer

    @classmethod
    def send_response(cls, current_url: str) -> Optional[requests.models.Response]:

        user_agent = cls.get_random_item('user-agent.txt')
        referer = cls.get_random_item('referer.txt')
        proxy_string = cls.get_random_item('proxies.txt')
        headers = {'user-agent': user_agent, 'referer': referer}
        response = requests.Session()

        if proxy_string:
            response.proxies = {"http": proxy_string, "https": proxy_string}
        try:
            resp = response.get(current_url, headers=headers, verify=False, timeout=30)
            return resp
        except Exception as e:
            logger.error(f'Запрос неудачный -  {current_url}  - {type(e)}\n{e}')
        return None

    @classmethod
    def get_ending(cls, number: int, ending_list: list[str]) -> str:
        number = number % 100
        if number >= 11 and number <= 19:
            ending = ending_list[2]
        else:
            i = number % 10
            if i == 1:
                ending = ending_list[0]
            elif i == 2 or i == 3 or i == 4:
                ending = ending_list[1]
            else:
                ending = ending_list[2]
        return ending

    @classmethod
    def get_start_driver(cls, url: str, headless: bool, browser: Optional[str] = None, size: Optional[bool] = None, fonts: Optional[bool] = None) -> Optional[WebDriver]:

        domen = cls.get_domen(url)
        driver = None

        for i in range(1, 4):

            user_agent = cls.get_random_item('user-agent.txt')
            proxy_string = cls.get_random_item('proxies.txt')

            # chrome
            if proxy_string:
                options_pr = {
                    # 'disable_capture': True,
                    'proxy': {
                        'http': proxy_string,
                        'https': proxy_string,
                        'no_proxy': 'localhost,127.0.0.1',
                    }
                }
            else: options_pr = {}
            opts = ChromeOptions()

            opts.add_experimental_option("detach", True)
            opts.add_experimental_option("excludeSwitches", ['enable-automation'])

            opts.add_argument("--start-maximized")

            opts.add_experimental_option('useAutomationExtension', False)
            opts.add_argument("--disable-blink-features")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument('--disable-software-rasterizer')

            # user-agent
            if browser: user_agent = browser
            opts.add_argument(f'user-agent={user_agent}')
            # console
            opts.add_argument('--log-level=3')
            opts.add_argument('--output=/dev/null')
            opts.add_argument('--disable-logger')
            # disable image
            # opts.add_argument('--blink-settings=imagesEnabled=false')
            # lang
            opts.add_argument('--lang=ru_RU')

            # disable fonts
            if fonts: opts.add_argument('--disable-remote-fonts')

            # disable certificate
            # opts.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])

            # disable infobar
            opts.add_argument("disable-infobars")
            opts.add_argument("--disable-extensions")
            opts.add_argument('--disable-notifications')

            if headless: opts.add_argument('--headless')
            # opts.add_argument('--headless')

            try:
                # cirilic domen
                cirilic_domen = re.search(r'\.[а-я]{2,}$', domen)
                if cirilic_domen or domen.startswith(('xn--', 'www.xn--')):
                    driver = webdriver_main.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
                else:
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts, seleniumwire_options=options_pr)
                    driver.request_interceptor = cls.interceptor
                if size: driver.set_window_size(480, 600)
                else: driver.set_window_size(1366, 768)

                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    'source': '''
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                        const newProto = navigator.__proto__;
                        delete newProto.webdriver;
                        navigator.__proto__ = newProto;
                '''
                })

                # timeout
                driver.set_page_load_timeout(100)
                driver.get(url)
                logger.info(f'Driver получен. Кол-во попыток - {i}')
                return driver

            except Exception as e:
                logger.error(f'{domen} -  {type(e)}\n{e}')
                if driver: driver.quit()

        return driver

    @classmethod
    def get_format_time(cls, seconds: int) -> str:
        res_text = 'Время работы скрипта программы - '

        if seconds < 1: res_text += str(round(seconds, 3)) + cls.get_ending(seconds, [' секунда ', ' секунды ', ' секунд '])

        seconds_in_day = 86400
        seconds_in_hour = 3600
        seconds_in_minute = 60

        seconds = round(seconds)
        days = seconds // seconds_in_day
        seconds = seconds - (days * seconds_in_day)

        hours = seconds // seconds_in_hour
        seconds = seconds - (hours * seconds_in_hour)

        minutes = seconds // seconds_in_minute
        seconds = seconds - (minutes * seconds_in_minute)

        if days:
            res_text += str(days) + cls.get_ending(days, [' день ', ' дня ', ' дней '])
        if hours:
            res_text += str(hours) + cls.get_ending(hours, [' час ', ' часа ', ' часов '])
        if minutes:
            res_text += str(minutes) + cls.get_ending(minutes, [' минута ', ' минуты ', ' минут '])
        if seconds:
            res_text += str(seconds) + cls.get_ending(seconds, [' секунда ', ' секунды ', ' секунд '])

        return res_text

    @classmethod
    def get_links_from_file(cls, file_name: str) -> list[str]:
        path_file = os.path.join(os.getcwd(), 'info', file_name)
        with open(path_file, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line and line != '\n']
        return links

    @classmethod
    def get_file_name(cls, domain: str) -> str:
        file_name = f'{domain}_{datetime.today().strftime("%d_%m_%Y_%H_%M")}'
        full_file_name = os.path.join(os.getcwd(), 'results', file_name)
        return full_file_name

    @classmethod
    def convert_cirillic_domain(cls, domain, url):
        domain_cirillic = re.search(r'\.[а-я]+$', url)
        if domain_cirillic:
            new_domen = domain.encode('idna').decode('utf-8')
            url = url.replace(domain, new_domen)
            domain = new_domen
        return url, domain
