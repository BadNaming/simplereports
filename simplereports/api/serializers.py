from django.contrib.auth import get_user_model
from rest_framework import serializers

from reports.models import Cabinet, Report, ReportTask

from .validators import validate_metrics

User = get_user_model()


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


# class ReportInfoSerializer(serializers.Serializer):
#     """
#     Сериализатор для получения инфы для создания задачи на отчет
#     """
#
#     cabinets = CabinetSerializer(many=True)
#     campaigns = CampaignSerializer(many=True)
#     metrics = serializers.ListField()


class CampaignSerializer(serializers.Serializer):
    """
    Сериализатор для метрик
    """
    campaign = serializers.IntegerField()
    shows = serializers.IntegerField()
    cpm = serializers.FloatField()
    clicks = serializers.IntegerField()
    ctr = serializers.FloatField()
    cpc = serializers.FloatField()
    goals = serializers.IntegerField()
    cr = serializers.IntegerField()
    cpa = serializers.FloatField()
    spent = serializers.FloatField()


class ReportSerializer(serializers.Serializer):
    """
    Сериализатор для выдачи отчета на сайте
    """
    campaigns = CampaignSerializer(many=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью User.
    """

    class Meta:
        model = User
        fields = ('id', 'email',
                  'first_name ', 'last_name',
                  'phone_number', 'vk_client_id',
                  'vk_client_secret')


class UserReportsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Report.
    """
    class Meta:
        model = Report
        fields = ('id', 'title',
                  'status',
                  'user', 'date',
                  'file_name', 'url')
