from django.db import models
from django.urls import reverse


class Page(models.Model):
    title = models.CharField(max_length=250, verbose_name='Title')
    description = models.TextField(verbose_name='Мета Описание')
    h_title = models.CharField(max_length=200, verbose_name='Заголовок')
    full_text = models.TextField(verbose_name='Текст страницы', blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    bool_menu = models.BooleanField(default=False, verbose_name='Добавлять в верхнее меню?')
    bool_footer_menu = models.BooleanField(default=False, verbose_name='Добавлять в нижнее меню?')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)

    def __str__(self):
        return self.h_title

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Страница (у)'
        verbose_name_plural = 'Страницы'
        ordering = ['pk']


class SiteMetric(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='Ключ')
    title = models.CharField(max_length=250, verbose_name='Название параметра', blank=True, null=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Параметр сайта'
        verbose_name_plural = 'Параметры сайта'
