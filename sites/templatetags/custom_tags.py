from django.template.defaulttags import register

from users.utils import titles


@register.filter
def get_item(dictionary, key):
    if isinstance(key, tuple):
        key = key[0]
    element = dictionary.get(key, '')
    if isinstance(element, str):
        return element.replace('www.', '')
    return element


@register.filter
def check_element(dictionary, key):
    if isinstance(key, tuple):
        key = key[0]
    if not dictionary.get('status_code'):
        if key in [item[0] for item in titles[2]] or key in [item[0] for item in titles[3]] or key in [item[0] for item in titles[4]]:
            return True
    if key in ['tehnologies', 'analitics', 'whois_registr', 'whois_servers', 'whois_age', 'whois_end_time', 'whois_end_plan']:
        element = dictionary.get(key)
        if not element:
            return True


@register.filter
def get_decode(str):
    return str.decode('utf-8')


@register.filter
def get_rus_domen(domen):
    if domen.startswith('xn--'):
        return domen.encode('utf-8').decode('idna')
    return domen


@register.filter
def get_block_class(field):
    class_el = ''
    if field.name == 'captcha':
        class_el += 'block-captcha '
    if field.errors:
        class_el += 'block-error'
    return class_el


@register.filter
def check_type_var(variable):
    if isinstance(variable, str):
        return True
    return False


@register.filter
def get_el_on_index(variable, index):
    return variable[index]


@register.filter
def get_icon_class(dict, item):
    result = ''
    key = item[0]
    value = dict.get(key)
    match key:
        case 'yandex_iks':
            try:
                value = int(value.replace('\xa0', ''))
            except: pass
            if isinstance(value, int) and value > 0:
                result = 'p-icon-success'
            elif isinstance(value, str) and 'не' not in value:
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'yandex_https' | 'yandex_turbo':
            if value and value == 'знак получен':
                result = 'p-icon-success'
            elif value and 'не' in value:
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'yandex_reviews':
            if value and value == 'есть':
                result = 'p-icon-success'
            elif value and value == 'нет':
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'yandex_reviews':
            if value and value == 'есть':
                result = 'p-icon-success'
            elif value and value == 'нет':
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'yandex_pages' | 'google_pages':
            try:
                value = int(value.replace('\xa0', ''))
            except: pass
            if isinstance(value, int) and value > 0:
                result = 'p-icon-success'
            elif value and value == 'js_ya_pages':
                result = 'p-js-load'
            elif value == '0' or isinstance(value, int):
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'verify':
            if value and value == 'cайт безопасен':
                result = 'p-icon-success'
            elif value and 'не' in value:
                result = 'p-icon-info'
            else: result = 'p-icon-error'
        case 'status_code':
            if value and '20' in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'code_site' | 'server' | 'tehnologies' | 'analitics' | 'title' | 'description' | 'keywords' | 'file_size' | 'request_time':
            if value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'lang' | 'robots_result' | 'sitemap_result':
            if value and 'не' in value:
                result = 'p-icon-error'
            elif value:
                result = 'p-icon-success'
            else: result = 'p-icon-info'
        case 'validator':
            if value and 'нет' in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'ip' | 'ip_country':
            if value and 'не' not in value and '-' not in value:
                result = 'p-icon-success'
            else: result = 'p-icon-info'
        case 'ssl' | 'redirect_www' | 'code_404' | 'link_404':
            if value and 'не' not in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'structure_sait':
            if value and 'H1 - 1' in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'count_words':
            if isinstance(value, int) and value > 100:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'external_links':
            if value and ('Индексируется: 0' in value or 'не' in value):
                result = 'p-icon-success'
            else: result = 'p-icon-info'
        case 'schema':
            if value == 'найдена':
                result = 'p-icon-success'
            elif value == 'jsfunc':
                result = 'p-js-load'
            elif value == 'не найдена':
                result = 'p-icon-error'
            else: result = 'p-icon-info'
        case 'content_adult':
            if value and 'не' in value:
                result = 'p-icon-success'
            else: result = 'p-icon-info'
        case 'favicon_url':
            if value and value.startswith(('http://', 'https://')):
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'compression':
            if value and 'включено' in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'
        case 'cache':
            if value and 'включён' in value:
                result = 'p-icon-success'
            elif value and 'не' in value:
                result = 'p-icon-info'
            else: result = 'p-icon-error'
        case 'viewport':
            if value and 'не' not in value:
                result = 'p-icon-success'
            else: result = 'p-icon-error'

    return result


@register.filter
def add_no_code_resp(item, current_site):
    if not current_site.get('status_code'):
        if 'Техническое состояние' in item:
            item += '<p>Код ответа сервера не получен.</p>'
    return item


@register.filter
def get_description_metric(descriptions, item):
    if isinstance(item, tuple):
        item = item[0]
    for desc in descriptions:
        if desc.key == item:
            return desc.description
    return ''
