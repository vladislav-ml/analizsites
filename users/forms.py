import re

from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')


class UserForgetForm(forms.Form):
    email = forms.EmailField(label='Введите email, который указывали при регистрации, на него будет выслан пароль:', widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'}))
    captcha = CaptchaField(label=('Введите капчу'))


class UserUpdatePassword(forms.Form):
    password = forms.CharField(label='Введите новый пароль', help_text='Пароль должен содержать латинские буквы и цифры, как минимум 8 символов', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повторите новый пароль', widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):
        password = self.cleaned_data.get('password')
        if not re.search(r'\d', password) or not re.search('[a-zA-Z]', password):
            raise forms.ValidationError('Пароль не содержит латинской буквы или цифры.')
        password2 = self.cleaned_data.get('password2')
        if len(password) < 8:
            raise forms.ValidationError('Пароль меньше 8 символов.')
        if password != password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return super(UserUpdatePassword, self).clean(*args, **kwargs)


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, widget=forms.EmailInput())
    image = forms.ImageField(label='Изображение', required=False, widget=forms.FileInput(), help_text=f'Максимальный размер не более {settings.MAX_SIZE_UPLOAD_IMAGE // 1024}kB')

    class Meta:
        model = User
        fields = ('email', 'image', 'first_name', 'last_name')

    def clean_image(self):
        image = self.cleaned_data['image']
        if image and image.size > settings.MAX_SIZE_UPLOAD_IMAGE:
            raise ValidationError(f'Превышен максимальный размер -  {settings.MAX_SIZE_UPLOAD_IMAGE // 1024}kB')
        return image


class UserDeleteForm(forms.ModelForm):
    captcha = CaptchaField(label='Введите капчу')

    class Meta:
        model = User
        fields = ('captcha', )
