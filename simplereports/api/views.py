import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .vk_config import (
    GENERAL_URL,
    GETUSER,
    GETPLANS,
    REQUEST_HEADERS,
    METRICS_VK
)


@api_view(['GET'])
def get_report(request):
    url = GENERAL_URL + GETPLANS
    plans = requests.get(url, headers=REQUEST_HEADERS).json()
    data = {'campaigns': []}
    for campaign in plans.get('items'):
        obj = dict()
        obj['campaign'] = campaign.get('id')
        metrics = campaign.get('total').get('base')
        for metric in METRICS_VK:
            obj[metric] = metrics.get(metric)
        data['campaigns'].append(obj)

    return Response(data)
