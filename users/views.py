import os
import re
from datetime import datetime
from urllib.parse import urlparse

import dateutil.parser
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, TemplateView,
                                  UpdateView, View)
from fpdf import FPDF

from analizsites.myredis import MyRedis

from .forms import (UserDeleteForm, UserForgetForm, UserLoginForm,
                    UserProfileForm, UserRegistrationForm)
from .utils import create_new_password, titles

User = get_user_model()


class UserRegistrationView(SuccessMessageMixin, CreateView):
    """ Регистрация пользователя """
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    success_message = 'Успешно зарегистрированы.'


class UserLoginView(SuccessMessageMixin, LoginView):
    """ Авторизация аользователя """
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_message = 'Успешно вошли в аккаунт'

    # def get_success_url(self):
    #     return reverse_lazy('profile', args=(self.request.user.pk,))


class UserForgetPassword(View):
    """ Врсстановление пароля """
    def get(self, request):
        form = UserForgetForm()
        return render(request, 'users/forget.html', {'form': form})

    def post(self, request):
        form = UserForgetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email)
            if user:
                new_password = create_new_password()
                subject_mail = f'Восстановление пароля на сайте - {request.META["HTTP_HOST"]}'
                content_mail = render_to_string('users/email_forget_pass.html',
                                                {'site': request.META["HTTP_HOST"], 'new_password': new_password})
                res_mail = self.send_email_user(subject_mail, content_mail, email)
                if res_mail:
                    user[0].set_password(new_password)
                    user[0].save()
                    messages.success(request, 'Пароль успешно обновлён! Проверьте почту!')
                    return redirect('login')
                else:
                    messages.error(request, 'Ошибка! Попробуйте позже.')
            else:
                messages.error(request, 'Данного email не найдено!')
        return render(request, 'users/forget.html', {'form': form})

    def send_email_user(self, subject_mail, content_mail, email):
        txt_mail = re.sub(r'<[^>]+>', '', content_mail, flags=re.S)
        try:
            res_email = send_mail(subject_mail, txt_mail, settings.EMAIL_USER_FULL, [email], fail_silently=False, html_message=content_mail)
            return res_email
        except Exception as e:
            print(type(e), e)


class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """ Вывод профиля """
    model = User
    template_name = 'users/profile.html'
    form_class = UserProfileForm
    success_message = 'Успешно обновлено!'

    def get_success_url(self):
        return reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserUpdatePswd(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    """ Обновление пароля """
    template_name = 'users/profile.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('update_pswd')
    success_message = 'Пароль успешно обновлен'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['update_pswd'] = True
        return context


class UserSitesView(LoginRequiredMixin, TemplateView):
    """ Вывод сайтов """
    template_name = 'users/profile.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['check_sites'] = True
        context['sites'] = self.get_user_sites()
        return context

    def get_user_sites(self):
        sites_arr = []
        sites = self.request.user.sites
        if sites:
            sites_arr = set(n.strip().rstrip('/') for n in sites.split(',') if n)
        return sites_arr


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """ Удаление учетной записи """
    template_name = 'users/profile.html'
    extra_context = {'check_delete': True}
    success_url = reverse_lazy('home')
    success_message = 'Аккаунт пользователя успешно удален'
    form_class = UserDeleteForm

    def get_object(self, queryset=None):
        return self.request.user


class CreatePDF(View):
    """ Создание PDF файла """
    def get(self, request):
        return render(request, '404.html', {})

    def post(self, request):
        url = request.POST.get('url')
        if not url or not url.startswith(('http://', 'https://')):
            return HttpResponse('Не найден url')
        domain = urlparse(url).hostname
        if not domain:
            return HttpResponse('Неверный url')
        result_redis = MyRedis.get_redis(domain)
        if not result_redis:
            return HttpResponse('Не найден домен.')
        full_path_pdf, href_pdf = self.generate_pdf(result_redis, domain)
        MyRedis.update_redis_value(domain, 'path_pdf', href_pdf)
        return HttpResponse(href_pdf)

    def generate_pdf(self, result_redis, domain):
        write_if_true = ['tehnologies', 'analitics', 'whois_end_plan']
        title_page = f'<p><b><center>Анализ сайта «{result_redis["url"]}»</center></b></p>'
        pdf = FPDF()
        path_font_regular = os.path.join(os.getcwd(), 'fonts', 'noto', 'Noto Sans_Regular.ttf')
        path_font_bold = os.path.join(os.getcwd(), 'fonts', 'noto', 'Noto Sans_Bold.ttf')
        pdf.add_font("Sans", style="", fname=path_font_regular, uni=True)
        pdf.add_font("Sans", style="B", fname=path_font_bold, uni=True)
        pdf.set_font("Sans", size=22)
        pdf.add_page()

        pdf.write_html(title_page)
        check_status_code = True
        for block in titles:
            for item in block:
                if isinstance(item, str):
                    pdf.set_font_size(18)
                    end_item = f'<p><b>{item}</b></p>'
                    pdf.write_html(end_item)
                else:
                    pdf.set_font_size(14)
                    if item[0] in write_if_true:
                        if not result_redis.get(item[0]):
                            continue
                    end_item = f'<p>{item[1]} <b>{result_redis.get(item[0], "-")}</b></p>'
                    pdf.write_html(end_item)
                    if item[0] == 'whois_status' and result_redis.get(item[0]) == 'свободен':
                        break
                    if item[0] == 'status_code' and not result_redis.get(item[0]):
                        pdf.write_html('Код ответа сервера не получен.')
                        check_status_code = False
                        break
            if not check_status_code:
                break

        create_time = f'<p>Дата проверки: {dateutil.parser.parse(result_redis["time"]).strftime("%d.%m.%Y %H:%M")}</p>'
        pdf.write_html(create_time)

        path_url = f'{domain}_{dateutil.parser.parse(result_redis["time"]).strftime("%d_%m_%Y_%H_%M")}.pdf'

        # mkdir dir
        create_date = datetime.now()
        create_year = str(create_date.year)
        create_month = str(create_date.month)
        create_day = str(create_date.day)

        os.makedirs(os.path.join(os.getcwd(), 'media', 'pdf', create_year, create_month, create_day), exist_ok=True)

        full_path_pdf = os.path.join(os.getcwd(), 'media', 'pdf', create_year, create_month, create_day, path_url)
        href_pdf = os.path.join(os.sep, 'media', 'pdf', create_year, create_month, create_day, path_url)

        # remove other version document
        self.remove_other_version_document(domain)

        pdf.output(full_path_pdf)
        return full_path_pdf, href_pdf

    def remove_other_version_document(self, domain):
        count_dots = domain.count('.') + 1
        path_dir = os.path.join(os.getcwd(), 'media', 'pdf')
        for root, dirs, files in os.walk(path_dir):
            for name_file in files:
                if domain in name_file and count_dots == name_file.count('.'):
                    full_path_file = os.path.join(root, name_file)
                    os.remove(full_path_file)
