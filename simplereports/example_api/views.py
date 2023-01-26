import requests
import json
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from example_ads.models import Case

URL_CODE = 'https://oauth.vk.com/authorize'
URL_TOKEN = 'https://oauth.vk.com/access_token'
URL_MY_TOKEN = 'https://target-sandbox.my.com/api/v2/oauth2/token.json'

@api_view(['GET', 'POST'])
def callback(request):
    get_params = request.query_params
    code = get_params.get('code')
    token = get_params.get('token')
    if code and not token:
        case = Case.objects.create(code=code)
        params = {
            'client_id': '51489312',
            'client_secret': 'Av2uV1Mz3ZXZ8zt2wk0z',
            'redirect_uri': 'https://test-junglegym.online/api/',
            'code': code,
            'scope': 'ads'

        }
        response = requests.get(URL_TOKEN, params=params)
        current_token = json.loads(response.text)
        case.response = current_token
        case.save()
        token = current_token['access_token']
        case.token = token
        case.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def mytarget_callback(request):
    template = 'example_ads/callback.html'
    get_params = request.query_params
    code = get_params.get('code')
    user_id = get_params.get('user_id')
    case = Case.objects.create(code=code)
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': 'fwppFISONxVknpbU',
        'permanent': 'true',
    }
    response = requests.post(URL_MY_TOKEN, data=params)
    current_token = json.loads(response.text)
    case.response = current_token
    case.user_id = user_id
    case.save()
    case.my_token = current_token['access_token']
    case.save()

    context = {'user_id': case.user_id,
               'token': case.my_token,
               'response': current_token,
               }

    return render(request, template, context)
