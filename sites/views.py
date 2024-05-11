import json
import re
from datetime import date, datetime
from urllib.parse import urlparse

import dateutil.parser
import requests
import tldextract
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, TemplateView, View

from analiz_site import ParsingLinks
from analizsites import schema_markup, yandex_pages
from analizsites.common import CommonMethod
from analizsites.myredis import MyRedis
from users.utils import titles

from .forms import AnalizForm, ContactForm
from .models import Page, SiteMetric
from .utils import MixinGetMethod

User = get_user_model()


class HomeView(ListView):
    """ Вывод главной страницы """
    context_object_name = 'main_page'
    template_name = 'sites/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['sites'] = MyRedis.get_redis_all(16)
        return context

    def get_queryset(self):
        index_page = cache.get('index_page')
        if not index_page:
            index_page = get_object_or_404(Page, pk=1)
            cache.set('index_page', index_page, 60 * 60 * 24)
        return index_page


class PageView(LoginRequiredMixin, View):
    """ Вывод страницы """

    def get(self, request, slug):
        form = False
        if slug == 'nashi-kontakty':
            form = ContactForm()
        page = get_object_or_404(Page, slug=slug)
        return render(request, 'sites/page.html', {'page': page, 'form': form})

    def post(self, request, slug):
        page = get_object_or_404(Page, slug=slug)
        form = ContactForm(request.POST)
        if form.is_valid():
            name_contact = form.cleaned_data['name_contact']
            email_contact = form.cleaned_data['email_contact']
            text_contact = form.cleaned_data['text_contact']
            response = self.send_message_tg(name_contact, email_contact, text_contact)
            if response.status_code == 200:
                messages.add_message(request, messages.SUCCESS, 'Благодарим за заявку!')

            else:
                messages.add_message(request, messages.ERROR, 'Ошибка! Попробуйте позже.')
            return redirect(request.META['HTTP_REFERER'])

        return render(request, 'sites/page.html', {'page': page, 'form': form})

    def send_message_tg(self, name, email, text):
        message = f'Сообщение с сайта: {self.request.META["HTTP_HOST"]}\nИмя: {name}\nEmail: {email}\nТекст: {text}'
        url_tg = f'https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage'
        data = {
            'chat_id': settings.TG_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
        response = requests.post(url_tg, data=data)
        return response


class AnalizSiteView(MixinGetMethod):
    """ Анализ сайта """

    def post(self, request):

        #  check limit analize
        limit = self.check_limit(request)
        if limit is False: return HttpResponse(json.dumps({'code': '400', 'text': 'Дневной лимит проверки сайтов использован.'}))

        form = AnalizForm(request.POST)
        if not request.user.is_authenticated:
            if not form.is_valid():
                return HttpResponse(json.dumps({'code': '400', 'text': 'Ошибка в капче или url'}))
        schema = request.POST.get('schema', '')
        url = request.POST.get('url', '').lower()
        url = schema + url
        domain = tldextract.extract(url).registered_domain
        if not domain or not url.startswith(('http://', 'https://')):
            return HttpResponse(json.dumps({'code': '400', 'text': f'Неверный url: {url}'}))

        # build url
        url, domain = self.build_url(domain, url)
        url, domain = CommonMethod.convert_cirillic_domain(domain, url)

        # get data
        res_dict = MyRedis.get_redis(domain)
        schema_bool = False
        ya_pages_bool = False
        screen_bool = True

        if not res_dict:
            parse_obj = ParsingLinks(screen_bool, schema_bool, ya_pages_bool)
            parse_obj.main([url])
            res_dict = parse_obj.result_redis
            res_dict['time'] = res_dict['time'].strftime('%d.%m.%Y %H:%M')

        else:
            delta_time = datetime.now() - dateutil.parser.parse(res_dict['time'])
            days = delta_time.days
            if days >= 1:

                # dop. parametrs no doing screen
                if days <= 3 and res_dict.get('img'): screen_bool = False

                ParsingLinks(screen_bool, schema_bool, ya_pages_bool).main([url])

        if request.user.is_authenticated:
            self.update_sites(request.user.pk, url)

        response = HttpResponse({'url': url})
        if settings.LIMIT_COUNT:
            self.set_cookies(response, limit)

        return response

    def check_limit(self, request):
        if not settings.LIMIT_COUNT: return True
        current_day = date.today().strftime('%Y-%m-%d')
        user_day = request.COOKIES.get('analiz_day') if request.COOKIES.get('analiz_day') else ''
        user_count = request.COOKIES.get('analiz_count') if request.COOKIES.get('analiz_count') else 0
        if current_day == user_day:
            if int(user_count) >= settings.LIMIT_COUNT:
                return False
        else: user_count = 0
        return user_count

    def update_sites(self, id, url):
        current_user = self.request.user
        if url not in current_user.sites:
            current_user.sites += f',{url}'
            current_user.save()

    def build_url(self, domain, url):
        subdomain = tldextract.extract(url).subdomain
        url = urlparse(url).scheme + '://'
        if subdomain:
            domain = f'{subdomain}.{domain}'
            url += domain
        else: url += domain
        return url, domain

    def set_cookies(self, response, limit):
        response.set_cookie('analiz_day', date.today(), max_age=86400, expires=None, path='/')
        response.set_cookie('analiz_count', int(limit) + 1, max_age=86400, expires=None, path='/')

    # def is_ajax(self, request):
    #     return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class SiteFromRedisView(View):
    """ Вывод сайта """
    def get(self, request, domain):
        descriptions = cache.get('descriptions')
        if not descriptions:
            descriptions = SiteMetric.objects.all()
            cache.set('descriptions', descriptions, 60 * 60)
        res_dict = MyRedis.get_redis(domain)
        if not res_dict:
            return render(request, '404.html', {})
        delta_time = datetime.now() - dateutil.parser.parse(res_dict['time'])
        count_days = delta_time.days if delta_time.days >= 1 else False
        res_dict['time'] = dateutil.parser.parse(res_dict['time']).strftime('%d.%m.%Y %H:%M')
        context = {
            'url': domain,
            'current_site': res_dict,
            'count_days': count_days,
            'titles': titles,
            'descriptions': descriptions
        }
        return render(request, 'sites/single.html', context=context)


class OptionWithAjax(MixinGetMethod):
    """ Получение Schema Markup из google and yande pages by using AJAX """
    def post(self, request):
        response = 'не получено'
        url = request.POST.get('url')
        number = int(request.POST.get('number'))
        domen = urlparse(url).hostname
        if number == 1:
            ya_pages = yandex_pages.YandexPages.get_yandex_pages(url, site_save=False)
            response = self.save_value_redis(domen, ya_pages, 'yandex_pages')
        elif number == 2:
            schema_res = schema_markup.SchemaMarkup.get_schema_markup(url, site_save=False)
            response = self.save_value_redis(domen, schema_res, 'schema')
        return HttpResponse(response)

    def save_value_redis(self, domen, result, field):
        if result is False: result = 'не получено'
        MyRedis.update_redis_value(domen, field, result)
        return result


class RobotsView(TemplateView):
    """ Файл robots.txt """
    template_name = 'sites/robots.txt'
    content_type = 'text'


class MapHtmlView(ListView):
    """ Карта сайта в формате html """
    template_name = 'sites/sitemap.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return MyRedis.get_redis_all()


class MapXmlView(ListView):
    """ Карта сайта в формате xml """
    template_name = 'sites/sitemap.xml'
    context_object_name = 'posts'
    paginate_by = 10000
    content_type = 'text/xml'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        host = self.request.META.get('HTTP_HOST')
        schema = self.request.scheme
        context['full_host'] = schema + '://' + host
        return context

    def get_queryset(self):
        return MyRedis.get_redis_all()
