from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

METRICS = (
    ('impressions', 'Показы'),
    ('CPM', 'Стоимость тысячи показов'),
    ('clicks', 'Клики по креативам'),
    ('spent', 'Траты')
)

STATUS = (
    ('one_answer', 'Единственный возможный ответ'),
    ('many_answers', 'Множество возможных ответов'),
    ('string_answer', 'Строчный ввод'),
    ('corresp_answer', 'Таблица соответствия')
)


class Cabinet(models.Model):
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='cabinets',
    #     verbose_name='Владелец кабинета'
    # )
    ext_id = models.IntegerField(
        verbose_name='Внешний ID кабинета'
    )
    ext_name = models.CharField(
        max_length=100,
        verbose_name='Внешнее название кабинета'
    )


class Campaign(models.Model):
    ext_id = models.IntegerField(
        verbose_name='Внешний ID кампании'
    )
    ext_name = models.CharField(
        max_length=100,
        verbose_name='Внешнее название кампании'
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        related_name='campaigns',
        verbose_name='Кабинет принадлежности'
    )


class ReportTask(models.Model):
    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания задачи'
    )
    cabinets = models.TextField()
    campaigns = models.TextField()
    metrics = models.TextField()


class TemporaryData(models.Model):
    code = models.CharField(max_length=1000, null=True)
    token = models.CharField(max_length=1000, null=True)
    response = models.TextField(null=True, blank=True)


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
