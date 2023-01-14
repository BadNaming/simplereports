from django.shortcuts import render

def index(request):
    template = 'example_ads/index.html'
    context = {}
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