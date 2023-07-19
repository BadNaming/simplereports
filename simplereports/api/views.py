import requests

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from exceptions import (
    DataNotReceivedException,
    InvalidDataException,
    ResponseNotRecievedException,
)
from reports.models import AdPlan, Report
from .serializers import ReportSerializer, UserReportsSerializer
from .services import (
    add_statistics_to_db,
    create_report,
    get_ad_plans,
    get_daily_data,
)
from .vk_config import GENERAL_URL, GETPLANS, METRICS_VK, REQUEST_HEADERS

User = get_user_model()


@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        openapi.Parameter(
            "start_date",
            openapi.TYPE_OBJECT,
            description="Дата начала периода",
            type=openapi.TYPE_STRING,
            required=False,
        )
    ],
    responses={
        200: openapi.Response(
            "Успешное выполнение запроса",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "ad_plan_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "date": openapi.Schema(
                            type=openapi.TYPE_STRING, format="date"
                        ),
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

    Параметры:
    - start_date (необязательный) - дата начала периода, за который
    запрашивается статистика.

    Разрешения:
    - Пользователь должен быть авторизован.

    Алгоритм работы:
    1. Отправка запроса к API ВКонтакте для получения списка
       рекламных кампаний (ad_plans.json).
    2. Если запрос не успешен (статус не равен 200), вернуть ошибку
       с соответствующим статусом и сообщением.
    3. Получение данных о рекламных кампаниях из ответа API и
       обновление модели AdPlan в базе данных.
    4. Отправка запроса к API ВКонтакте для получения ежедневной
       статистики (ad_plans/day.json).
    5. Если запрос не успешен (статус не равен 200), вывести сообщение
       об ошибке.
    6. Получение данных о ежедневной статистике из ответа API и
       формирование списка статистик.
    7. Создание/обновление моделей Statistics в базе данных
       с использованием полученных данных.
    8. Возврат ответа со списком обновленных статистик и статусом 200.
    """
    user = request.user

    ad_plans_data = get_ad_plans(user)

    if request.body:
        start_date = request.data.get("start_date")

    if isinstance(ad_plans_data, Response):
        return Response(ad_plans_data.data, status=ad_plans_data.status_code)

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

    if isinstance(statistics, Response):
        return Response(statistics.data, status=statistics.status_code)

    query = add_statistics_to_db(statistics)
    return Response(query, status=HTTP_200_OK)


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "start_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата начала периода",
            ),
            "end_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата окончания периода",
            ),
            "ad_plans": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Список идентификаторов рекламных кампаний",
                ),
            ),
        },
        required=["start_date", "end_date"],
    ),
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
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes((JSONParser,))
def create_report_for_the_period(request):
    """
    Формирует отчет по кампаниям учетной записи
    за указанный период времени и возвращает его в виде файла.

    Параметры:
    - start_date - дата начала периода, за который запрашивается статистика (обязательный).
    - end_date - дата окончания периода, за который запрашивается статистика (обязательный).
    - ad_plans - список идентификаторов рекламных кампаний,
    по которым запрашивается статистика (необязательный).
    """

    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    if not start_date or not end_date:
        raise DataNotReceivedException()
    campaigns = request.data.get("ad_plans", [])
    return create_report(request.user, start_date, end_date, campaigns)


@api_view(["GET"])
def get_report(request):
    """
    Получаем статистику по всем кампаниям
    учетной записи по адресу ads.vk.com/api/v2/statistics/ad_plans/summary.json
    сериализуем и выдаем ее на эндпоинт v1/report/
    """
    url = GENERAL_URL + GETPLANS
    data = {"campaigns": []}
    if requests.get(url, headers=REQUEST_HEADERS).status_code != HTTP_200_OK:
        raise ResponseNotRecievedException()

    plans = requests.get(url, headers=REQUEST_HEADERS).json()
    for campaign in plans.get("items"):
        obj = dict()
        obj["campaign"] = campaign.get("id")
        metrics = campaign.get("total").get("base")
        for metric in METRICS_VK:
            obj[metric] = metrics.get(metric)
        data["campaigns"].append(obj)

    serializer = ReportSerializer(data=data)

    if not serializer.is_valid():
        if serializer.errors:
            raise InvalidDataException(serializer.errors)
        raise DataNotReceivedException()

    return Response(serializer.data, status=HTTP_200_OK)


@api_view(["GET"])
def download_report(request, *args, **kwargs):
    """
    Функция загружает XLS файл с готовым отчетом.
    """
    report_id = kwargs.get("pk")
    report = Report.objects.filter(id=report_id).get()
    with open(report.url / report.file_name, "rb") as file:
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
