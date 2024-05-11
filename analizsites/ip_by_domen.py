import os
import socket

import IP2Location

from sitemain.settings import logger

from .common import CommonMethod


class Ip:

    """ Получение ip домена и страны """
    @classmethod
    def get_ip_by_domen(cls, url: str) -> dict:
        ip, ip_country = '', '-'
        domen = CommonMethod.get_domen(url)
        try:
            ip = socket.gethostbyname(domen)
        except socket.gaierror as error:
            logger.error(f'{domen} - {type(error)}\n{error}')
        if ip:
            database = IP2Location.IP2Location(os.path.join('data', 'IPV6-COUNTRY.BIN'))
            rec = database.get_all(ip)
            ip_country = rec.country_long
        if not ip: ip = 'не удалось получить'
        return {'ip': ip, 'ip_country': ip_country}
