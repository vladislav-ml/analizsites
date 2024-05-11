from urllib.parse import urlparse

from .common import CommonMethod


class Redirect_www:

    """ Редирект на www """

    @classmethod
    def get_redirect_www(cls, url: str) -> dict:
        scheme = urlparse(url).scheme
        domen = CommonMethod.get_domen(url)

        current_url = f'{scheme}://{domen}'

        redirect_bez_www = cls.checking_status_code(current_url)
        if not redirect_bez_www: return {}

        # response with wwww
        current_url = f'{scheme}://www.{domen}'

        redirect_with_www = cls.checking_status_code(current_url)
        if not redirect_with_www: return {}

        if redirect_bez_www == redirect_with_www:
            redirect_result = 'Перенаправление настроено.'
        else:
            redirect_result = 'Перенаправление не настроено.'

        return {'redirect_www': redirect_result}

    @classmethod
    def checking_status_code(cls, url: str) -> str | bool:
        resp = CommonMethod.send_response(url)
        if resp and resp.status_code == 200:
            return resp.url
        return False
