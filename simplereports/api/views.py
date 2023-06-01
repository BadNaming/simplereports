import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.exceptions import NotFound


from exceptions import DataNotReceivedException, InvalidDataException
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
    if requests.get(url,
                    headers=REQUEST_HEADERS).status_code == HTTP_404_NOT_FOUND:
        raise NotFound('Страница не найдена')

    plans = requests.get(url, headers=REQUEST_HEADERS).json()
    for campaign in plans.get('items'):
        obj = dict()
        obj['campaign'] = campaign.get('id')
        metrics = campaign.get('total').get('base')
        for metric in METRICS_VK:
            obj[metric] = metrics.get(metric)
        data['campaigns'].append(obj)

    serializer = ReportSerializer(data=data)

    if not serializer.is_valid():
        if serializer.errors:
            raise InvalidDataException(serializer.errors)
        raise DataNotReceivedException()

    return Response(serializer.data)
