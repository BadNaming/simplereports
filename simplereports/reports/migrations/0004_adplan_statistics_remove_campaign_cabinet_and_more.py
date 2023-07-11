# Generated by Django 4.1.5 on 2023-07-09 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0003_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_plan_id', models.CharField(max_length=10, verbose_name='id рекламной кампании во ВКонтакте')),
                ('name', models.CharField(max_length=300, verbose_name='Название рекламной кампании')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ad_plans', to=settings.AUTH_USER_MODEL, verbose_name='Владелец рекламных кампаний')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('shows', models.IntegerField(verbose_name='Показы')),
                ('clicks', models.IntegerField(verbose_name='Клики')),
                ('spent', models.CharField(max_length=50, verbose_name='Расходы')),
                ('ad_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='reports.adplan', verbose_name='Статистика за сутки')),
            ],
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='cabinet',
        ),
        migrations.DeleteModel(
            name='ReportTask',
        ),
        migrations.DeleteModel(
            name='TemporaryData',
        ),
        migrations.AlterField(
            model_name='report',
            name='url',
            field=models.FilePathField(path='/Users/kapshtyk/Code/simplereports/simplereports/reports'),
        ),
        migrations.DeleteModel(
            name='Cabinet',
        ),
        migrations.DeleteModel(
            name='Campaign',
        ),
    ]
