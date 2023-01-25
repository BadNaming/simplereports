import time

import requests
import json
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from reports.models import Cabinet, Campaign, METRICS, ReportTask, TemporaryData
from .mixins import ForbiddenMethodsMixin
from .serializers import ReportInfoSerializer, ReportTaskSerializer
from .vk_methods import ACCOUNTS_PARAMS, CAMPAIGNS_PARAMS, GENERAL_URL, GETACCOUNTS, GETCAMPAIGNS, TOKEN


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
    url = GENERAL_URL+GETACCOUNTS
    get_cabinets = requests.get(url, params=ACCOUNTS_PARAMS).json()
    for cab in get_cabinets.get('response'):
        create_cab, success = Cabinet.objects.get_or_create(
            ext_id=cab.get('account_id'),
            ext_name=cab.get('account_name')
        )
        obj = dict()
        obj['id'] = create_cab.id
        obj['ext_id'] = create_cab.ext_id
        obj['ext_name'] = create_cab.ext_name
        data['cabinets'].append(obj)

    data['campaigns'] = []
    cabs = []
    url = GENERAL_URL+GETCAMPAIGNS
    for cabinet in data['cabinets']:
        cabs.append(cabinet.get('ext_id'))
    for cab in cabs:
        params = CAMPAIGNS_PARAMS
        params['account_id'] = cab
        get_campaigns = requests.get(url, params=params).json()
        response = get_campaigns.get('response')
        if response:
            for campaign in get_campaigns.get('response'):
                create_camp, success = Campaign.objects.get_or_create(
                    ext_id=campaign.get('id'),
                    ext_name=campaign.get('name'),
                    cabinet=get_object_or_404(Cabinet, ext_id=cab)
                )
                obj = dict()
                obj['ext_id'] = create_camp.ext_id
                obj['ext_name'] = create_camp.ext_name
                obj['cabinet'] = create_camp.cabinet.pk
                data['campaigns'].append(obj)
        time.sleep(1)


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
