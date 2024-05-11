# -*- coding: utf-8 -*-
import concurrent.futures
import re
import sys
from datetime import datetime
from time import time

import requests
from urllib3.exceptions import InsecureRequestWarning

from analizsites import (certificate, google_pages, info_site, ip_by_domen,
                         page_404, redirect_www, save_results, schema_markup,
                         screen_site, validator, verify_site_google, whois,
                         yandex_iks, yandex_pages)
from analizsites.common import CommonMethod
from analizsites.myredis import MyRedis
from sitemain.settings import logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ParsingLinks():
    file_name = None

    def __init__(self, screen_bool: bool = True, schema_bool: bool = True, ya_pages_bool: bool = True):
        self.screen_bool = screen_bool
        self.schema_bool = schema_bool
        self.ya_pages_bool = ya_pages_bool
        self.result_redis = dict()

    def main(self, urls: list[str]) -> None:
        t_start = time()

        for url in urls:
            logger.info(f'\n\n=======================\nанализ url - {url}')

            self.result_redis['url'] = url
            self.result_redis['time'] = datetime.now()

            domen = CommonMethod.get_domen(url)

            # cirillic_domen
            if __name__ == '__main__':
                url, domen = CommonMethod.convert_cirillic_domain(domen, url)

            self.file_name = CommonMethod.get_file_name(domen)

            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                r1 = executor.submit(screen_site.ScreenSite.get_screenshot_site, url, self.result_redis['time'], self.screen_bool)
                r2 = executor.submit(info_site.InfoSite.get_info_site, url, self.file_name)
                r3 = executor.submit(yandex_iks.YandexIks.get_yandex_iks, url)
                r4 = executor.submit(yandex_pages.YandexPages.get_yandex_pages, url, self.ya_pages_bool)
                r5 = executor.submit(google_pages.GooglePages.get_google_pages, url)
                r6 = executor.submit(validator.Validator.get_validator_html, url)
                r7 = executor.submit(whois.Whois.get_whois, url)
                r8 = executor.submit(ip_by_domen.Ip.get_ip_by_domen, url)
                r9 = executor.submit(certificate.Certificate.get_certificate, url)
                r10 = executor.submit(redirect_www.Redirect_www.get_redirect_www, url)
                r11 = executor.submit(verify_site_google.VerifyGoogle.verify_site_google, url)
                r12 = executor.submit(page_404.Page_404.send_response_404, url)
                r13 = executor.submit(schema_markup.SchemaMarkup.get_schema_markup, url, self.schema_bool)

            self.result_redis = {
                **self.result_redis,
                **r1.result(),
                **r2.result(),
                **r3.result(),
                **r4.result(),
                **r5.result(),
                **r6.result(),
                **r7.result(),
                **r8.result(),
                **r9.result(),
                **r10.result(),
                **r11.result(),
                **r12.result(),
                **r13.result(),
            }

            # save redis
            MyRedis.save_redis(url, self.result_redis, self.screen_bool)

            # save file
            # save_results.SaveResult.write_result_csv(self.file_name, self.result_redis)

            t_end = time()
            print(f'Время анализа - {t_end - t_start} c.')
            logger.info(f'Время анализа {url} - {t_end - t_start:.2f} c.')


if __name__ == '__main__':
    time_start = time()
    urls = []
    links_file = CommonMethod.get_links_from_file('links.txt')
    if len(sys.argv) > 1:
        current_links = [sys.argv[1]]
    elif links_file:
        current_links = links_file
    elif urls:
        current_links = urls
    else:
        print('Нет url!')
        sys.exit()

    parse_obj = ParsingLinks()
    parse_obj.main(current_links)

    time_end = time()
    print(CommonMethod.get_format_time(time_end - time_start))
