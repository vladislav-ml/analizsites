from django import template

from sites.models import Page

register = template.Library()


@register.inclusion_tag('inc/menu_tpl.html')
def show_menu(menu_class='', type_menu=1):
    if type_menu == 1:
        pages = Page.objects.filter(bool_menu=True)
    else:
        pages = Page.objects.filter(bool_footer_menu=True)
    return {'pages': pages, 'menu_class': menu_class, 'type_menu': type_menu}
