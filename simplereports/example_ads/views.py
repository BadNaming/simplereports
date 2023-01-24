from django.shortcuts import render
import secrets


def index(request):
    template = 'example_ads/index.html'
    state = secrets.token_urlsafe(20)
    context = {'state': state}
    return render(request, template, context)


def index2(request):
    template = 'example/index.html'
    context = {}
    return render(request, template, context)

def index3(request):
    template = 'example/index3.html'
    context = {}
    return render(request, template, context)

def about(request):
    template = 'example_ads/about.html'
    context = {}
    return render(request, template, context)

def constructor(request):
    template = 'example_ads/constructor.html'
    context = {}
    return render(request, template, context)

def report(request):
    template = 'example_ads/report.html'
    context = {}
    return render(request, template, context)