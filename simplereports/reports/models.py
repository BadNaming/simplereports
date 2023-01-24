from django.db import models

from users.models import User

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
