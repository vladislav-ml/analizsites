from captcha.fields import CaptchaField
from django import forms


class ContactForm(forms.Form):

    name_contact = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя*'}))
    email_contact = forms.EmailField(max_length=200, widget=forms.EmailInput(attrs={'placeholder': 'Ваш email*'}))
    text_contact = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Текст сообщения*'}))
    captcha = CaptchaField(label=('Введите капчу:'))


class AnalizForm(forms.Form):
    PROTOCOLS = (
        ('https://', 'https://'),
        ('http://', 'http://')
    )

    schema = forms.CharField(max_length=8, widget=forms.Select(choices=PROTOCOLS))
    url = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'placeholder': 'Введите домен'}))
    captcha = CaptchaField(label=('Введите капчу:'))
