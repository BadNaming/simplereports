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
        'Authorization': 'Bearer vzaTe6vgpb9PI9izFBXnGFaTJM727IJFRpWJLw5hLj2O5mRVnEhNhfQ9qzYaSNq5P8maB5UfqWlyfPbOpZzXKPbhTcHRmuoTpQKd6Q2vIscyGaTbW73QxjpXGqa90GQu0dsoXi7JAKmVdmsGYmgCaSiekcJabm0PENwHr1HUdt5icEa0zdFVxhuPvldo16J3oz6jEQSJBmq6ec5r4z4YCI8xhkRqjU',
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
