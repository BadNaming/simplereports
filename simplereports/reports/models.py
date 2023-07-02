from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AdPlan(models.Model):
    """
    Модель рекламных кампаний.
    Данные для создания записи в БД берутся
    из ответа на запрос к GET /api/v2/ad_plans.json.
    Attrs:
    - ad_plan_id: уникальный идентификатор рекламной кампании
    в рамках ВКонтакте
    - name: название рекламной кампании
    - user: владелец рекламной кампании
    """
    ad_plan_id = models.CharField(
        max_length=10,
        verbose_name='id рекламной кампании во ВКонтакте')
    name = models.CharField(
        max_length=300,
        verbose_name='Название рекламной кампании')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ad_plans',
        verbose_name='Владелец рекламных кампаний')


class Statistics(models.Model):
    """
    Модель для выгрузки статистики из ВКонтакте.
    1 запись - статистика за 1 сутки по 1 рекламной кампании.
    Attrs:
    - ad_plan: рекламная кампания
    - date: дата
    - shows: показы
    - clicks: клики
    - goals: целевые показатели
    - spent: расходы
    """
    ad_plan = models.ForeignKey(
        AdPlan,
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name='Статистика за сутки')
    date = models.DateField(verbose_name='Дата')
    shows = models.IntegerField(verbose_name='Показы')
    clicks = models.IntegerField(verbose_name='Клики')
    spent = models.CharField(verbose_name='Расходы')


class Report(models.Model):
    """
    Модель отчета. Используется для сохранения готового отчета
    в базе и последующего скачивания в XLS в личном кабинете.
    """
    REPORT_STATUS_CHOICES = [
        ('process', 'В процессе формирования'),
        ('ready', 'Сформирован'),
        ('error', 'Ошибка формирования')]
    title = models.CharField(
        max_length=100,
        verbose_name='Заголовок отчета')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Автор отчета')
    status = models.CharField(
        max_length=100,
        choices=REPORT_STATUS_CHOICES,
        default='process')
    date = models.DateTimeField(
        verbose_name='Дата формирования отчета',
        auto_now_add=True)
    file_name = models.CharField(
        max_length=100,
        verbose_name='Название файла')
    url = models.FilePathField(
        path=settings.REPORTS_ROOT,
        allow_files=True)
