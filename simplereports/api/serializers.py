from rest_framework import serializers

from reports.models import Cabinet, Campaign, ReportTask
from .validators import validate_metrics


class ReportTaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для постановки задачи на отчет
    """

    cabinets = serializers.ListField()
    campaigns = serializers.ListField()
    metrics = serializers.ListField(validators=[validate_metrics, ])

    class Meta:
        model = ReportTask
        fields = ('cabinets', 'campaigns', 'metrics')


class CabinetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Cabinet
        fields = ('id', 'ext_id', 'ext_name')


class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = '__all__'


class ReportInfoSerializer(serializers.Serializer):
    """
    Сериализатор для получения инфы для создания задачи на отчет
    """

    cabinets = CabinetSerializer(many=True)
    campaigns = CampaignSerializer(many=True)
    metrics = serializers.ListField()


class Report(serializers.ModelSerializer):
    """
    Сериализатор для выдачи отчета на сайте
    """
    pass
