import requests
from django.shortcuts import render
import secrets

from .models import Case


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


def mytarget_campaings():
    headers = {
        'Authorization': 'Bearer NeNxx9fYYNg5ULI54nFUzTFFiavMoly2v9ZiykGQRgWPZkP2KDzHtcJ0iUX6ioMN0jOUPewSY0a9wTLGbapMMjRh5jIuR2ibhPX60TzADXsqV9Qd1TcrIaqKXDu6vQHyBscjiwA3jRaQgkjLdzAfVBNbaMNS9a9nWcrhakohTZSyqkcaf07LkIrlQR2HTPWDOBDqKSldYj7h6MOjytxiCG3z8cW0knehu7jDe30mY4NUFh3U7e1aXLhpNYyg',
    }
    campaigns = requests.get(
        'https://target-sandbox.my.com/api/v2/campaigns.json', headers=headers
    )
    status = campaigns.status_code
    return f'Статус: {status} Ответ: {campaigns.json()}'


def report_mytarget(request):
    template = 'example_ads/report_mytarget.html'
    context = {'report': mytarget_campaings()}
    return render(request, template, context)
