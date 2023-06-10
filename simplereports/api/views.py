from exceptions import (DataNotReceivedException, InvalidDataException,
                        ResponseNotRecievedException)

import requests
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from reports.models import Report

from .serializers import ReportSerializer, UserReportsSerializer
from .vk_config import GENERAL_URL, GETPLANS, METRICS_VK, REQUEST_HEADERS


@api_view(['GET'])
def get_report(request):
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


@api_view(['GET'])
def download_report(request, *args, **kwargs):
    """
    Функция загружает XLS файл с готовым отчетом.
    """
    report_id = kwargs.get('pk')
    report = Report.objects.filter(id=report_id).get()
    with open(report.url/report.file_name, 'rb') as file:
        response = HttpResponse(file, content_type='text/xls')
    response['Content-Disposition'] = f'attachment; filename={report.file_name}'
    return response


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Обрабатывает запросы только от авторизованного пользователя.
    Методы list и retrive отдают только те отчеты,
    которые принадлежат юзеру.
    """
    serializer_class = UserReportsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(
            user=self.request.user)
