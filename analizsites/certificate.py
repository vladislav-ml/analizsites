import re
import socket
from datetime import datetime

from OpenSSL.SSL import Connection, Context, SSLv3_METHOD, TLSv1_2_METHOD

from .common import CommonMethod


class Certificate:

    """ Сертификат сайта """

    @classmethod
    def get_certificate(cls, url: str) -> dict:

        domain = CommonMethod.get_domen(url)
        # cirillic domen
        my_current_domen_cirillic = re.search(r'\.[а-я]{2,}$', domain)
        if my_current_domen_cirillic:
            domain = domain.encode('idna').decode('utf-8')

        try:
            ssl_connection_setting = Context(SSLv3_METHOD)
        except ValueError:
            ssl_connection_setting = Context(TLSv1_2_METHOD)

        ssl_connection_setting.set_timeout(5)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((domain, 443))
            except Exception:
                current_date_ssl = 'Сайт не доступен по HTTPS.'
                return {'ssl': current_date_ssl}
            c = Connection(ssl_connection_setting, s)
            c.set_tlsext_host_name(str.encode(domain))
            c.set_connect_state()
            c.do_handshake()

            # get parametrs
            cert = c.get_peer_certificate()

            current_date = datetime.strptime(str(cert.get_notAfter().decode('utf-8')), '%Y%m%d%H%M%SZ').strftime('%d.%m.%Y')
            if not cert.has_expired():
                current_date_ssl = 'Сайт доступен по HTTPS. Срок действия сертификата до ' + current_date
            else:
                current_date_ssl = 'Сайт доступен по HTTPS. Истек срок действия сертификата:' + current_date

            c.shutdown()
            s.close()
            return {'ssl': current_date_ssl}
