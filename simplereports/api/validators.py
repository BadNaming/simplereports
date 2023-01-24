from django.core.validators import ValidationError

from reports.models import METRICS

def validate_metrics(values):
    check_list = [{i[0]:i[1]} for i in METRICS]
    for v in values:
        if v not in check_list:
            raise ValidationError('Недопустимая метрика')