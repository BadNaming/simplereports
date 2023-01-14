from django.shortcuts import render

def index(request):
    template = 'example_ads/index.html'
    context = {}
    return render(request, template, context)