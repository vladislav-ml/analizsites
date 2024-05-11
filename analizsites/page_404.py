import string
from urllib.parse import urljoin

from bs4 import BeautifulSoup as BS

from sitemain.settings import logger

from .common import CommonMethod


class Page_404:

    """ Код ответа 404 при несуществующей странице, имеется ли ссылка для перехода. """

    @classmethod
    def send_response_404(cls, url: str) -> dict:
        try:
            domen = CommonMethod.get_domen(url)
            code_404, link_404 = 'не получен код 404', 'ссылка не найдена'
            numbers = string.digits + '/'
            query_str = numbers * 7
            current_url = urljoin(url, query_str)
            resp = CommonMethod.send_response(current_url)
            if resp is None: return {}
            if resp.status_code == 404:
                code_404 = 'получен код 404'
                soup = BS(resp.text, 'html.parser')
                links = soup.find_all('a', attrs={'href': True})
                for link in links:
                    href = link.get('href')
                    if domen in href or href.startswith('/'):
                        link_404 = 'ссылка найдена'
                        break
        except Exception as e:
            logger.error(f'{type(e)} - {e}')

        return {'code_404': code_404, 'link_404': link_404}
