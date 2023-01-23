from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from reports.models import Cabinet, Campaign, METRICS, ReportTask
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
    data['metrics'] = ['one_answer', 'many_answers']
    serializer = ReportInfoSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return Response(
        serializer.data, status=status.HTTP_200_OK
    )