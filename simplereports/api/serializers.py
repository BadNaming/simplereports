from django.contrib.auth import get_user_model
from rest_framework import serializers

from reports.models import Report, Statistics

from .validators import validate_metrics

User = get_user_model()

from rest_framework import serializers


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
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "vk_client_id",
            "vk_client_secret",
            "vk_client_token",
        )


class UserReportsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Report.
    """

    class Meta:
        model = Report
        fields = ("id", "title", "status", "user", "date", "file_name", "url")


class StatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для работы с моделью Statistics.
    """

    class Meta:
        model = Statistics
        fields = ("ad_plan", "date", "shows", "clicks", "spent")


class DailySerializer(serializers.Serializer):
    daily_statistics = StatisticsSerializer(many=True)
