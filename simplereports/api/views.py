import requests
import json
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from reports.models import Cabinet, Campaign, METRICS, ReportTask, TemporaryData
from .mixins import ForbiddenMethodsMixin
from .serializers import ReportInfoSerializer, ReportTaskSerializer


class ReportTaskViewset(ForbiddenMethodsMixin, viewsets.ModelViewSet):
    serializer_class = ReportTaskSerializer
    queryset = ReportTask.objects.all()

    def perform_create(self, serializer):
        cabs_list = map(str, serializer.data.get('cabinets'))
        cabs_for_save = ','.join(cabs_list)
        camps_list = map(str, serializer.data.get('campaigns'))
        camps_for_save = ','.join(camps_list)
        mets_for_save = ', '.join(serializer.data.get('metrics'))
        ReportTask.objects.create(
            cabinets=cabs_for_save,
            campaigns=camps_for_save,
            metrics=mets_for_save
        )



@api_view(['GET'])
def get_info(request):
    data = dict()

    data['cabinets'] = []
    cabinet_queryset = Cabinet.objects.all()
    for cabinet in cabinet_queryset:
        obj = dict()
        obj['id'] = cabinet.id
        obj['ext_id'] = cabinet.ext_id
        obj['ext_name'] = cabinet.ext_name
        data['cabinets'].append(obj)

    data['campaigns'] = []
    campaign_queryset = Campaign.objects.all()
    for campaign in campaign_queryset:
        obj = dict()
        obj['ext_id'] = campaign.ext_id
        obj['ext_name'] = campaign.ext_name
        obj['cabinet'] = campaign.cabinet.id
        data['campaigns'].append(obj)
    data['metrics'] = []
    for metric in METRICS:
        data['metrics'].append({metric[0]: metric[1]})
    serializer = ReportInfoSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return Response(
        serializer.data, status=status.HTTP_200_OK
    )


@api_view(['GET', 'POST'])
def callback(request):
    get_params = request.query_params
    code = get_params.get('code')
    token = get_params.get('token')
    if code and not token:
        tem_data = TemporaryData.objects.create(code=code)
        params = {
            'client_id': '51521857',
            'client_secret': 'J5dnCVJIR4J7691XcGi5',
            'redirect_uri': 'https://test-simplereports.ru/api/v1/vk/',
            'code': code,
            'scope': 'ads'

        }
        response = requests.get('https://oauth.vk.com/access_token', params=params)
        current_token = json.loads(response.text)
        tem_data.response = current_token
        tem_data.save()
        token = current_token['access_token']
        tem_data.token = token
        tem_data.save()
    return Response(status=status.HTTP_200_OK)
