from django.urls import path

from .views import (AnalizSiteView, HomeView, MapHtmlView, MapXmlView,
                    OptionWithAjax, PageView, RobotsView, SiteFromRedisView)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('option_ajax/', OptionWithAjax.as_view(), name='option_ajax'),
    path('robots.txt', RobotsView.as_view(), name='robots'),
    path('analiz/', AnalizSiteView.as_view(), name='analiz'),
    path('karta-saita/', MapHtmlView.as_view(), name='karta-saita'),
    path('sitemap.xml', MapXmlView.as_view(), name='sitemap'),
    path('page/<str:slug>/', PageView.as_view(), name='page'),
    path('<str:domain>/', SiteFromRedisView.as_view(), name='site'),
]
