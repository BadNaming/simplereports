# Generated by Django 4.1.5 on 2023-07-11 13:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reports", "0008_alter_adplan_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="adplan",
            unique_together={("ad_plan_id", "user")},
        ),
        migrations.AlterUniqueTogether(
            name="statistics",
            unique_together={("ad_plan", "date")},
        ),
    ]