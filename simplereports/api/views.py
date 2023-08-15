import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exceptions import (
    DataNotReceivedException,
)
from reports.models import AdPlan, Report, Statistics
from .serializers import StatisticsSerializer, UserReportsSerializer
from .services import (
    add_statistics_to_db,
    create_report,
    get_ad_plans,
    get_daily_data,
)

User = get_user_model()


@api_view(["DELETE"])
# TODO УДАЛИТЬ ЭТОТ СЛАВНЫЙ ЭНДПОЙНТ!!!
def clear_database(request):
    """
    Очищает базу данных от всех записей.
    """
    AdPlan.objects.all().delete()
    Report.objects.all().delete()
    User.objects.filter(email="johndoe@email.com").delete()
    return Response(status=204)


@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Bearer токен",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "start_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата начала периода",
                example="2021-01-01",
            )
        },
    ),
    responses={
        200: openapi.Response(
            "Успешное выполнение запроса",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "ad_plan_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                        "shows": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "clicks": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "spent": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        ),
        "4xx": openapi.Response(
            "Ошибка клиента",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        "5xx": openapi.Response(
            "Ошибка сервера",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes((JSONParser,))
def add_daily_data(request, start_date=None, *args, **kwargs):
    """
    Получает ежедневную статистику с указанной в теле запроса даты
    для всех рекламных кампаний, связанных с аккаунтом пользователя в VK,
    и сохраняет ее в базе данных.

    Parameters:
    - start_date (необязательный) - дата начала периода, за который
    запрашивается статистика.

    Permissions:
    - Пользователь должен быть авторизован.

    Returns:
    - Возврат ответа со списком обновленных статистик и статусом 200.
    """
    user = request.user

    ad_plans_data = get_ad_plans(user)

    if request.body:
        start_date = request.data.get("start_date")

    if isinstance(ad_plans_data, Response):
        return ad_plans_data

    for campaign in ad_plans_data.get("items"):
        AdPlan.objects.update_or_create(
            ad_plan_id=campaign.get("id"),
            user=user,
            name=campaign.get("name"),
        )

    statistics = get_daily_data(
        AdPlan.objects.filter(user=user).values_list("ad_plan_id", flat=True),
        user,
        start_date,
    )

    logging.info(statistics)

    if isinstance(statistics, Response):
        return statistics

    query = add_statistics_to_db(statistics)
    return query


@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Bearer токен",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "start_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата начала периода",
                example="2021-01-01",
            ),
            "end_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата окончания периода",
                example="2021-01-01",
            ),
            "ad_plans": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Список идентификаторов рекламных кампаний",
                    example=[808686, 676865],
                ),
            ),
        },
        required=["start_date", "end_date"],
    ),
    responses={
        200: openapi.Response(
            "Успешное выполнение запроса",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                    "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                    "file_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "url": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        "4xx": openapi.Response(
            "Ошибка клиента",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        "5xx": openapi.Response(
            "Ошибка сервера",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes((JSONParser,))
def create_report_for_the_period(request):
    """
    Формирует отчет по кампаниям учетной записи
    за указанный период времени и возвращает сериализованные данные из модели Report,
    касающиеся этого отчета. Возвращает ошибку в случае некорректных данных.

    Parameters:
    - start_date - дата начала периода, за который запрашивается статистика (обязательный).
    - end_date - дата окончания периода, за который запрашивается статистика (обязательный).
    - ad_plans - список идентификаторов рекламных кампаний,
    по которым запрашивается статистика (необязательный).
    """

    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    if not start_date or not end_date:
        raise DataNotReceivedException()
    campaigns = request.data.get("ad_plans", "")

    return create_report(request.user, start_date, end_date, campaigns)


@swagger_auto_schema(
    method="GET",
    responses={
        200: openapi.Response(
            "Успешное выполнение запроса",
            schema=openapi.Schema(
                type=openapi.TYPE_FILE,
                description="Excel-файл с отчетом",
            ),
        ),
        "4xx": openapi.Response(
            "Ошибка клиента",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        "5xx": openapi.Response(
            "Ошибка сервера",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def download_report(request, *args, **kwargs):
    """
    Функция загружает XLS файл с готовым отчетом.
    """
    report_id = kwargs.get("pk")
    report = Report.objects.filter(id=report_id).get()
    with open(report.url, "rb") as file:
        response = HttpResponse(file, content_type="text/xls")
        response["Content-Disposition"] = f"attachment; filename={report.file_name}"
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
        return Report.objects.filter(user=self.request.user)


class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StatisticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Statistics.objects.filter(ad_plan__user=self.request.user)
