from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from .models import Page, SiteMetric


class PageAdminForm(forms.ModelForm):
    full_text = forms.CharField(required=False, widget=CKEditorUploadingWidget())

    class Meta:
        model = Page
        fields = '__all__'


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('id', 'h_title', 'bool_menu',)
    list_display_links = ('id', 'h_title',)
    list_editable = ('bool_menu',)
    fields = ('id', 'title', 'slug', 'description', 'h_title', 'full_text', 'created_at', 'bool_menu', 'bool_footer_menu')
    readonly_fields = ('id', 'created_at')


class SiteMetricAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = SiteMetric
        fields = '__all__'


class SiteMetricAdmin(admin.ModelAdmin):
    form = SiteMetricAdminForm
    list_display = ('title', 'key',)
    list_display_links = ('title',)


admin.site.register(Page, PageAdmin)
admin.site.register(SiteMetric, SiteMetricAdmin)
