from datetime import datetime

import dateutil.parser
import tldextract
from bs4 import BeautifulSoup as BS

from sitemain.settings import logger

from .common import CommonMethod


class Whois:

    """ Получение данных whois """

    @classmethod
    def get_whois(cls, url: str) -> dict:
        result_redis = {'whois_status': 'не удалось проверить.'}
        domen_extract = tldextract.extract(url)
        domen = domen_extract.registered_domain

        current_url = f'https://whois.ru/{domen}'

        resp = CommonMethod.send_response(current_url)

        if not resp:
            logger.warning(f'{current_url} - Не удалось получить response')
            return result_redis

        soup = BS(resp.text, 'html.parser')
        try:
            result = soup.find('pre', attrs={'class': 'raw-domain-info-pre'}).text
        except:
            return result_redis

        if not result or result == 'Object does not exist':
            result_redis['whois_status'] = 'домен свободен'
        else:
            result_redis = cls.options_domain_busy(result, result_redis)

        return result_redis

    @classmethod
    def get_age_domain(cls, creation_date: str) -> dict:
        result_redis = {}
        create_date = dateutil.parser.parse(creation_date)
        domain_delta = datetime.now() - create_date
        age_days = domain_delta.days
        if not age_days // 365:
            result_redis['whois_age'] = f'{age_days} {CommonMethod.get_ending(age_days, ["день","дня","дней"])}'
        else:
            years = age_days // 365
            remaining_days = age_days % 365
            result_redis['whois_age'] = f'{years} {CommonMethod.get_ending(years, ["год","года","лет"])}, {remaining_days} {CommonMethod.get_ending(remaining_days, ["день","дня","дней"])}'
        return result_redis

    @classmethod
    def options_domain_busy(cls, result: str, result_redis: dict) -> dict:
        result_redis['whois_status'] = 'занят'
        name_servers = ''
        creation_date, time_end_domen, time_plan_domen = '', '', ''
        result_arr = result.split('\n')
        for item in result_arr:
            if not item: continue
            item_arr = item.split(':')
            key = item_arr[0].strip().lower()
            if 'no entries found for the selected source' in key or 'no match for domain' in key:
                result_redis['whois_status'] = 'свободен'
                break

            if key == 'Registrar'.lower():
                result_redis['whois_registr'] = item_arr[1].strip()
            if key == 'Name Server'.lower() or key == 'nserver':
                name_servers += f'{item_arr[1].strip()}, '
            if key == 'Creation Date'.lower() or key == 'created':
                creation_date = item_arr[1].strip()
            if key == 'paid-till' or key == 'expiration date' or key == 'registry expiry date':
                time_end_domen = item_arr[1].strip()
            if key == 'free-date':
                time_plan_domen = item_arr[1].strip()
        if name_servers:
            name_servers = name_servers.strip(', ')
            result_redis['whois_servers'] = name_servers
        if creation_date:
            domain_age_dict = cls.get_age_domain(creation_date)
            result_redis = {**result_redis, **domain_age_dict}
        if time_end_domen:
            time_end_domen = dateutil.parser.parse(time_end_domen).strftime('%d.%m.%Y')
            result_redis['whois_end_time'] = time_end_domen
        if time_plan_domen:
            time_plan_domen = dateutil.parser.parse(time_plan_domen).strftime('%d.%m.%Y')
            result_redis['whois_end_plan'] = time_plan_domen

        return result_redis
