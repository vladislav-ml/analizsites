import tldextract
from django.template.defaulttags import register


@register.filter
def get_domen_profile(url):
    domen_extract = tldextract.extract(url)
    domen = domen_extract.registered_domain
    return domen
