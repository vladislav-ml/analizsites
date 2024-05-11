import random

titles = [

    [
        'Показатели сайта',
        ('yandex_iks', 'Яндекс ИКС:'),
        ('yandex_https', 'Яндекс знак: Защищённое соединение:'),
        ('yandex_turbo', 'Яндекс знак: Турбо-страницы:'),
        ('yandex_reviews', 'Яндекс отзывы:'),
        ('yandex_pages', 'Индексация в яндексе:'),
        ('google_pages', 'Индексация в google:'),
        ('verify', 'Безопасный просмотр Google:'),
    ],
    [
        'Состояние домена',
        ('whois_status', 'Информация о домене. Статус:'),
        ('whois_registr', 'Регистратор:'),
        ('whois_servers', 'Name servers:'),
        ('whois_age', 'Возраст домена:'),
        ('whois_end_time', 'Дата окончания срока регистрации:'),
        ('whois_end_plan', 'Дата освобождения домена:'),
    ],
    [
        'Техническое состояние сайта',
        ('status_code', 'Код ответа сервера:'),
        ('code_site', 'Кодировка сайта:'),
        ('lang', 'Язык сайта:'),
        ('robots_result', 'Наличие файла robots.txt:'),
        ('sitemap_result', 'Наличие карты сайта в xml формате:'),
        ('validator', 'Валидация html:'),
        ('ip', 'Ip адрес:'),
        ('ip_country', 'Страна:'),
        ('ssl', 'SSL сертификат:'),
        ('redirect_www', 'Редирект c WWW:'),
        ('server', 'Название сервера:'),
        ('tehnologies', 'Используемые технологии:'),
        ('analitics', 'Системы аналитики:'),
        ('code_404', 'Код ответа страницы 404:'),
        ('link_404', 'Ссылка со страницы 404:'),
    ],
    [
        'Внутреняя оптимизация',
        ('title', 'Title:'),
        ('description', 'Description:'),
        ('structure_sait', 'Структура сайта:'),
        ('count_words', 'Количество слов на странице:'),
        ('keywords', 'Ключевые слова:'),
        ('external_links', 'Внешние ссылки:'),
        ('schema', 'Микроразметка Schema.org:'),
        ('content_adult', 'Контент для взрослых:'),
        ('file_size', 'Размер страницы:'),
        ('favicon_url', 'Favicon:'),
    ],
    [
        'Скорость загрузки сайта',
        ('request_time', 'Время загрузки сайта:'),
        ('compression', 'Сжатие ресурсов:'),
        ('cache', 'Кеш браузера:'),
        ('viewport', 'Атрибут viewport:'),
    ]
]


def create_new_password():
    alphas = "abcdefghijklmnopqrstuvwxyz"
    alphas_cap = alphas.upper()
    numbers = "12345678901234567890123456"
    special_chars = "!@#$%^&*()_+/!@#$%^&*()_+/"
    password_characters = [alphas, alphas_cap, numbers, special_chars]
    new_password = ""
    for i in range(10):
        n = random.randint(0, 3)
        chars_used = password_characters[n]
        char = chars_used[random.randint(0, 25)]
        new_password += char
    return new_password
