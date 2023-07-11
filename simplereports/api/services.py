from django.db.models import Max
from django.utils import timezone

from reports.models import Statistics


def get_last_date(ad_plans):
    """
    Получаем последнюю дату в БД для статистики пользователя
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
