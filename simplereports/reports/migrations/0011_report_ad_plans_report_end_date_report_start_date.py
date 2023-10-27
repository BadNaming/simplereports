# Generated by Django 4.1.5 on 2023-10-24 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0010_alter_report_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="ad_plans",
            field=models.ManyToManyField(
                to="reports.adplan", verbose_name="Рекламные кампании"
            ),
        ),
        migrations.AddField(
            model_name="report",
            name="end_date",
            field=models.DateField(
                null=True, verbose_name="Дата окончания периода"
            ),
        ),
        migrations.AddField(
            model_name="report",
            name="start_date",
            field=models.DateField(
                null=True, verbose_name="Дата начала периода"
            ),
        ),
    ]