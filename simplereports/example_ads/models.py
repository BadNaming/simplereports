from django.db import models
from users.models import User


class Case(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField(null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    my_token = models.TextField(null=True, blank=True)
    user_id = models.TextField(null=True, blank=True)
    time = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)


class Cabinet(models.Model):
    account_id = models.IntegerField()
    client_id = models.IntegerField()


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    status = models.IntegerField()


class DateStat(models.Model):
    date = models.DateField()
    impressions = models.IntegerField(null=True, blank=True, default=0)
    clicks = models.IntegerField(null=True, blank=True, default=0)
    reach = models.IntegerField(null=True, blank=True, default=0)
    spent = models.CharField(max_length=100, null=True, blank=True)
    unique_views = models.IntegerField(null=True, blank=True, default=0)
