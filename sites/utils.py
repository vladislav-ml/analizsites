from django.shortcuts import render
from django.views.generic import View


class MixinGetMethod(View):

    def get(self, request):
        return render(request, '404.html', {})
