import datetime
import requests

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from exceptions import (
    DataNotReceivedException,
    InvalidDataException,
    ResponseNotRecievedException,
)
from reports.models import AdPlan, Report, Statistics
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .serializers import (
    ReportSerializer,
    UserReportsSerializer,
)
from .services import get_last_date
from .vk_config import (
    ADPLANS,
    GENERAL_URL,
    GETPLANS,
    GETPLANSDAY,
    METRICS_VK,
    REQUEST_HEADERS,
)


User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_daily_report(request, *args, **kwargs):
    """
    Получает ежедневную статистику для всех рекламных кампаний,
    связанных с аккаунтом пользователя во ВКонтакте.

    Разрешения:
    - Пользователь должен быть авторизован.

    Алгоритм работы:
    1. Получение токена доступа пользователя из базы данных.
    2. Отправка запроса к API ВКонтакте для получения списка
       рекламных кампаний (ad_plans.json).
    3. Если запрос не успешен (статус не равен 200), вернуть ошибку
       с соответствующим статусом и сообщением.
    4. Получение данных о рекламных кампаниях из ответа API и
       обновление модели AdPlan в базе данных.
    5. Получение минимальной даты из максимальных дат статистик для
       каждой рекламной кампании (используется функция get_last_date).
    6. Отправка запроса к API ВКонтакте для получения ежедневной
       статистики (ad_plans/day.json) с указанной минимальной датой.
    7. Если запрос не успешен (статус не равен 200), вывести сообщение
       об ошибке.
    8. Получение данных о ежедневной статистике из ответа API и
       формирование списка статистик.
    9. Создание/обновление моделей Statistics в базе данных
       с использованием полученных данных.
    10. Возврат ответа со списком обновленных статистик и статусом 200.
    """
    user = request.user
    token = user.vk_client_token

    if not token:
        return Response(
            {"error": "Не удалось получить токен VK пользователя"},
            status=HTTP_400_BAD_REQUEST,
        )

    ad_plans_response = requests.get(
        url=GENERAL_URL + ADPLANS,
        headers={"Authorization": f"Bearer {token}"},
    )
    if ad_plans_response.status_code != 200:
        return Response(
            {"error": "Не удалось получить список кампаний"},
            status=ad_plans_response.status_code,
        )

    ad_plans_data = ad_plans_response.json()
    if "items" not in ad_plans_data:
        return Response(
            {"error": "Некорректный формат ответа от сервера"},
            status=HTTP_400_BAD_REQUEST,
        )

    campaigns = []
    for campaign in ad_plans_data.get("items"):
        campaigns.append(campaign.get("id"))
        AdPlan.objects.update_or_create(
            ad_plan_id=campaign.get("id"),
            user=user,
            name=campaign.get("name"),
        )

    min_date = datetime.datetime.strftime(get_last_date(campaigns), "%d.%m.%Y")

    daily_data_response = requests.get(
        f"{GENERAL_URL}{GETPLANSDAY}"
        f"?id={','.join(list(map(str, campaigns)))}"
        f"&date_from={min_date}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(daily_data_response.json())
    if daily_data_response.status_code == 200:
        statistics = list(
            (
                {
                    campaign_data.get("id"): {
                        row.get("date"): {
                            "shows": row.get("base").get("shows"),
                            "clicks": row.get("base").get("clicks"),
                            "spent": row.get("base").get("spent"),
                        }
                        for row in campaign_data.get("rows")
                    }
                }
                for campaign_data in daily_data_response.json().get("items", [])
            )
        )

    if daily_data_response.status_code != 200:
        print(
            f"Не удалось получить ежедневную статистику для "
            f"кампаний {campaign}, код ответа: {daily_data_response.status_code}"
        )

    with transaction.atomic():
        statistics_to_create = [
            Statistics(
                ad_plan=AdPlan.objects.get(ad_plan_id=campaign_id),
                date=date,
                shows=metrics.get("shows"),
                clicks=metrics.get("clicks"),
                spent=metrics.get("spent"),
            )
            for campaign_data in statistics
            for campaign_id, daily_metrics in campaign_data.items()
            for date, metrics in daily_metrics.items()
        ]
    Statistics.objects.bulk_create(statistics_to_create)

    return Response({"statistics": statistics}, status=HTTP_200_OK)


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
