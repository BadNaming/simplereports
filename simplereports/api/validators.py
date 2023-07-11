from django.core.validators import ValidationError

from .vk_config import METRICS_VK


def validate_metrics(values):
    check_list = [i[0] for i in METRICS_VK]
    for v in values:
        if v not in check_list:
            raise ValidationError("Недопустимая метрика")
