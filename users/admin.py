from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'is_superuser', 'data_join')
    list_display_links = ('id', 'email')
    list_filter = ('is_superuser',)
    search_fields = ('email', )
    ordering = ('-data_join', )
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'image', 'sites')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_staff',
                    'is_superuser',
                    'is_active',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(get_user_model(), CustomUserAdmin)
