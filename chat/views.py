from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse('Its index page for testing urlpatterns')
