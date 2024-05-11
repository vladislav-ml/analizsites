from django import template

from sites.forms import AnalizForm

register = template.Library()


@register.inclusion_tag('inc/form_analiz_tpl.html', takes_context=True)
def show_form_analiz(context):
    form = AnalizForm()
    return {'form': form, 'context': context}
