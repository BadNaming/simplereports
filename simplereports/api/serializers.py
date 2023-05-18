from django.contrib.auth import get_user_model
from rest_framework import serializers

from reports.models import Cabinet, Campaign, ReportTask

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
