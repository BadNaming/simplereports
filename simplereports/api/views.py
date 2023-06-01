import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ReportSerializer
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
    data = {'campaigns': []}
    try:
        plans = requests.get(url, headers=REQUEST_HEADERS).json()
        if 'items' in plans.keys():
            for campaign in plans.get('items'):
                obj = dict()
                obj['campaign'] = campaign.get('id')
                metrics = campaign.get('total').get('base')
                for metric in METRICS_VK:
                    obj[metric] = metrics.get(metric)
                data['campaigns'].append(obj)
    except Exception:
        data['status'] = 'Данные не получены'
    serializer = ReportSerializer(data)

    return Response(serializer.data)
