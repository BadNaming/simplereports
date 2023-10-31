import datetime
import decimal
import time
from django.http import HttpResponse
import requests
from typing import Union
import os
from string import ascii_uppercase

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_201_CREATED,
)
import xlsxwriter

from reports.models import AdPlan, Report, Statistics
from api.serializers import (
    AdPlanSerializer,
    StatisticsSerializer,
    UserReportsSerializer,
)
from simplereports.settings import REPORTS_ROOT
from .vk_config import ADPLANS, GENERAL_URL, GETPLANSDAY


def get_token(user) -> Union[Response, str]:
    """
    Получаем токен VK пользователя из базы данных.

    :param user: Пользователь (экземпляр модели User).

    :return: При успешном запросе - токен VK пользователя,
    иначе объект Response с ошибкой.
    """
    token = user.vk_client_token

    if not token:
        return Response(
            {"error": "Не удалось получить токен VK пользователя"},
            status=HTTP_400_BAD_REQUEST,
        )

    return token


def get_last_date(ad_plans) -> datetime.date:
    """
    Получаем последнюю дату в БД для статистики пользователя.

    :param ad_plans: Список id кампаний в VK.

    :return: минимальная дата из максимальных дат по каждой из кампаний,
    за которые в базе данных есть статистика, либо 150 дней назад.
    """
    last_dates = (
        Statistics.objects.filter(ad_plan__ad_plan_id__in=ad_plans)
        .values("ad_plan__ad_plan_id")
        .annotate(max_date=Max("date"))
        .values_list("max_date", flat=True)
    )
    if last_dates:
        return min(last_dates)
    else:
        return timezone.now().date() - timezone.timedelta(days=150)


def get_ad_plans(user) -> Union[Response, dict]:
    """
    Получаем список рекламных кампаний пользователя из API VK.

    :param user: Пользователь (экземпляр модели User).

    :return: При успешном запросе - словарь, содержащий данные о
    рекламных кампаниях, иначе объект Response с ошибкой.
    """
    token = get_token(user)
    logger.info(f"получаем список кампаний пользователя: {user}")

    if isinstance(token, Response):
        return token

    ad_plans_response = requests.get(
        url=GENERAL_URL + ADPLANS,
        headers={"Authorization": f"Bearer {token}"},
    )
    if ad_plans_response.status_code != 200:
        return Response(
            {"error": "Не удалось получить список кампаний"},
            status=ad_plans_response.status_code,
        )

    if "items" not in ad_plans_response.json():
        return Response(
            {"error": "Некорректный формат ответа от сервера"},
            status=HTTP_400_BAD_REQUEST,
        )

    return ad_plans_response.json()


def add_ad_plans_to_db(user, ad_plans_data) -> Union[Response, dict]:
    """
    Добавляем рекламные кампании пользователя в базу данных.

    :param user: Пользователь (экземпляр модели User).
    :param ad_plans_data: Словарь, содержащий данные о рекламных кампаниях.

    :return: Сериализованные данные о рекламных кампаниях.
    """
    with transaction.atomic():
        ad_plans_to_create = [
            AdPlan(
                ad_plan_id=campaign.get("id"),
                user=user,
                name=campaign.get("name"),
            )
            for campaign in ad_plans_data.get("items")
        ]
    ad_plans = AdPlan.objects.bulk_create(
        ad_plans_to_create,
        update_conflicts=True,
        unique_fields=["ad_plan_id", "user"],
        update_fields=["name"],
    )

    if not ad_plans:
        return Response(
            {"error": "Не удалось добавить кампании в базу данных"},
            status=HTTP_400_BAD_REQUEST,
        )

    serialized_data = AdPlanSerializer(ad_plans_to_create, many=True).data
    return serialized_data


def get_daily_data(campaigns, user, start_date=None) -> Union[Response, list]:
    """
    Получаем ежедневную статистику для рекламных кампаний.

    :param campaigns: Список id кампаний в VK.
    :param user: Пользователь (экземпляр модели User).
    :param start_date: Дата, начиная с которой нужно получить статистику.

    :return: При успешном запросе - список, содержащий данные о
    ежедневной статистике, иначе объект Response с ошибкой.
    """
    token = get_token(user)

    if isinstance(token, Response):
        return token

    if start_date and datetime.datetime.strptime(
        start_date, "%Y-%m-%d"
    ).date() < datetime.date(2022, 9, 1):
        start_date = "2022-09-01"

    if not start_date:
        start_date = datetime.datetime.strftime(get_last_date(campaigns), "%Y-%m-%d")

    logger.info(
        f"{GENERAL_URL}{GETPLANSDAY}"
        f"?id={','.join(list(map(str, campaigns)))}"
        f"&date_from={start_date}",
    )
    daily_data_response = requests.get(
        f"{GENERAL_URL}{GETPLANSDAY}"
        f"?id={','.join(list(map(str, campaigns)))}"
        f"&date_from={start_date}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if daily_data_response.status_code != 200:
        return Response(
            {
                "error": (
                    f"Не удалось получить ежедневную статистику для "
                    f"кампаний {campaigns}, код ответа: {daily_data_response.status_code}"
                )
            },
            status=daily_data_response.status_code,
        )
    statistics = list(
        (
            {
                campaign_data.get("id"): {
                    row.get("date"): {
                        "shows": row.get("base").get("shows"),
                        "clicks": row.get("base").get("clicks"),
                        "spent": float(row.get("base").get("spent")),
                    }
                    for row in campaign_data.get("rows")
                    if (
                        row.get("base").get("shows")
                        or row.get("base").get("clicks")
                        or float(row.get("base").get("spent"))
                    )
                }
            }
            for campaign_data in daily_data_response.json().get("items", [])
        )
    )
    return statistics


def check_statistics(statistics) -> Union[Response, dict]:
    result = []
    for i in statistics:
        if i and any(i.values()):
            result.append(i)
    return result


def add_statistics_to_db(statistics) -> Union[Response, dict]:
    """
    Добавляем статистику в базу данных.

    :param statistics: Список, содержащий данные о ежедневной статистике рекламных кампаний.

    :return: Сериализованные данные о ежедневной статистике или объект Response с ошибкой.
    """
    statistics = check_statistics(statistics)
    if not statistics:
        return Response(
            {"error": "Нет данных для добавления в базу данных за указаннй период"},
            status=HTTP_400_BAD_REQUEST,
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
    statistics = Statistics.objects.bulk_create(
        statistics_to_create,
        update_conflicts=True,
        unique_fields=["ad_plan", "date"],
        update_fields=["shows", "clicks", "spent"],
    )

    if not statistics:
        return Response(
            {"error": "Не удалось добавить статистику в базу данных"},
            status=HTTP_400_BAD_REQUEST,
        )

    serialized_statistics = StatisticsSerializer(statistics, many=True).data
    return Response(serialized_statistics, status=HTTP_201_CREATED)


def create_report(
    user, start_date, end_date, campaigns=None, metrics=None
) -> Union[Response, list]:
    """
    Создаем отчет по статистике рекламных кампаний.

    :param user: Пользователь (экземпляр модели User).
    :param start_date: Начальная дата для отчета в формате YYYY-MM-DD.
    :param end_date: Конечная дата для отчета в формате YYYY-MM-DD.
    :param ad_plans: Список рекламных кампаний (необязательный)

    :return: возвращает сериализованные данные из модели Report,
    касающиеся отчета, либо ошибку в случае некорректных данных.
    """
    start_date_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    ad_plans = get_ad_plans(user)

    if isinstance(ad_plans, Response):
        return ad_plans

    add_ad_plans_to_db(user, ad_plans)

    if campaigns:
        campaigns = AdPlan.objects.filter(
            user=user, ad_plan_id__in=campaigns
        ).values_list("ad_plan_id", flat=True)

    else:
        campaigns = AdPlan.objects.filter(user=user).values_list(
            "ad_plan_id", flat=True
        )

    is_exists = True
    daily_data = []
    for campaign_id in campaigns:
        if not Statistics.objects.filter(
            ad_plan__ad_plan_id=campaign_id,
            date__range=(start_date_datetime, end_date_datetime),
        ).exists():
            is_exists = False
            break
    if not is_exists:
        daily_data = get_daily_data(campaigns, user, start_date=start_date)

    if isinstance(daily_data, Response):
        return daily_data

    statistics = add_statistics_to_db(daily_data)
    statistics = Statistics.objects.filter(
        ad_plan__ad_plan_id__in=campaigns,
        date__range=(start_date, end_date),
    )

    report = create_excel_report(
        user, statistics, metrics, start_date, end_date, campaigns
    )

    if report.status == "ready":
        serializer = UserReportsSerializer(report)
        logging.info(f"отчет создан: {serializer.data}")
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(
        {"error": "Ошибка формирования отчета"},
        status=HTTP_400_BAD_REQUEST,
    )


def calculate_metrics(statistic, metric):
    if metric == "shows":
        return statistic.shows
    elif metric == "clicks":
        return statistic.clicks
    elif metric == "spend":
        return decimal.Decimal(statistic.spent)
    elif metric == "ctr":
        return int(statistic.clicks) / int(statistic.shows) if statistic.shows else 0
    elif metric == "cpm":
        return (
            decimal.Decimal(statistic.spent) / int(statistic.shows) * 1000
            if statistic.shows
            else 0
        )
    elif metric == "cpc":
        return (
            decimal.Decimal(statistic.spent) / int(statistic.clicks)
            if statistic.clicks
            else 0
        )


def create_excel_report(
    user, statistics, metrics=None, start_date=None, end_date=None, campaigns=None
):
    title = f"report_{user.first_name}_{user.last_name}_{int(time.time())}.xlsx".lower()
    logging.info(f"создаем отчет: {title}")

    logging.info(
        f"start_date: {start_date}, end_date: {end_date}, metrics: {metrics}, campaigns: {campaigns}"
    )

    report = Report.objects.create(
        title=title,
        user=user,
        status="process",
        file_name=title,
        date=timezone.now(),
        url=os.path.join(REPORTS_ROOT, "reports", title),
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
    )
    logging.info(f"Campaigns: {campaigns}")
    if campaigns:
        report.ad_plans.set(AdPlan.objects.filter(ad_plan_id__in=campaigns))
    logging.info(f"Report: {report}")
    possible_metrics = {
        "shows": "Показы",
        "clicks": "Клики",
        "spend": "Расход, руб.",
        "ctr": "CTR",
        "cpm": "CPM, руб.",
        "cpc": "CPC, руб.",
    }

    try:
        # Считаем порядковую номер буквы в английском алфвите, которая будет соответствовать последнему столбцу в отчете.
        calc_last_row = (
            len(metrics) + 2 if metrics else len(possible_metrics.keys()) + 2
        )
        workbook = xlsxwriter.Workbook(os.path.join(REPORTS_ROOT, "reports", title))
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({"bold": True})
        date_format = workbook.add_format({"num_format": "dd.mm.yyyy"})
        percentage_format = workbook.add_format({"num_format": "0.00%"})
        money_format = workbook.add_format({"num_format": "0.00"})

        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 15)
        # Динамически устанавливаем ширину столбцов в зависимости от количества метрик.
        worksheet.set_column(f"D:{ascii_uppercase[calc_last_row]}", 15)

        worksheet.merge_range(
            f"A1:{ascii_uppercase[calc_last_row]}1",
            f"Отчет для пользователя: {user.first_name} {user.last_name}",
            bold,
        )

        # Список столбцов, которые будут в отчете по умолчанию.
        default_headers = [
            "Кампания",
            "ID кампании VK",
            "Дата",
        ]

        additional_headers = {}
        # Если в запросе были переданы метрики, то добавляем их в список столбцов. Если метрик в запросе нет, то добавляем все возможные метрики.
        if metrics:
            for i in metrics:
                additional_headers[i] = possible_metrics[i]
        else:
            additional_headers = possible_metrics

        result_headers = default_headers + list(additional_headers.values())

        # Формируем заголовки для отчета.
        for col, header in enumerate(result_headers, start=0):
            worksheet.write(1, col, header, bold)

        # Формируем данные для отчета.
        for row, statistic in enumerate(statistics, start=2):
            worksheet.write(row, 0, statistic.ad_plan.name)
            worksheet.write(row, 1, statistic.ad_plan.ad_plan_id)
            worksheet.write_datetime(row, 2, statistic.date, date_format)
            # Добавляем данные по метрикам.
            for i in range(len(additional_headers.keys())):
                metric_name = list(additional_headers.keys())[i]
                metric_value = calculate_metrics(statistic, metric_name)
                worksheet.write_number(
                    row,
                    i + 3,
                    metric_value,
                    percentage_format
                    if metric_name == "ctr"
                    else money_format
                    if metric_name in ["cpm", "cpc"]
                    else None,
                )
        workbook.close()
        report.status = "ready"
        report.save()
    except Exception as e:
        logging.error(e)
        report.status = "error"
        report.save()
    return report
