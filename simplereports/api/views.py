import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from exceptions import DataNotReceivedException, InvalidDataException, ResponseNotRecievedException
from .serializers import ReportSerializer
from .vk_config import (
    GENERAL_URL,
    GETPLANS,
    REQUEST_HEADERS,
    METRICS_VK
)


@api_view(['GET'])
def get_report(request):
    """
    Получаем статистику по всем кампаниям
    учетной записи по адресу ads.vk.com/api/v2/statistics/ad_plans/summary.json
    сериализуем и выдаем ее на эндпоинт v1/report/
    """
    url = GENERAL_URL + GETPLANS
    data = {'campaigns': []}
    if requests.get(url,
                    headers=REQUEST_HEADERS).status_code != HTTP_200_OK:
        raise ResponseNotRecievedException()

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

    return Response(serializer.data, status=HTTP_200_OK)
