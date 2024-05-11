from django.contrib.auth.views import (LogoutView, PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from .views import (CreatePDF, UserDeleteView, UserLoginView, UserProfileView,
                    UserRegistrationView, UserSitesView, UserUpdatePswd)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('create_pdf/', CreatePDF.as_view(), name='create_pdf'),
    path('profile/delete/', UserDeleteView.as_view(), name='delete'),
    path('profile/update/', UserUpdatePswd.as_view(), name='update_pswd'),
    path('profile/sites/', UserSitesView.as_view(), name='current_sites'),

    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html', email_template_name='users/password_reset_email.html', success_url=reverse_lazy('password_reset_done')), name='password_reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),

    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
