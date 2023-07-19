from django.contrib import admin
from django.db import models

from .models import Statistics, AdPlan, Report


class StatisticsAdmin(admin.ModelAdmin):
    list_display = ("id", "ad_plan", "date", "shows", "clicks", "spent")


class AdPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "ad_plan_id", "name", "user", "get_total_statistics")

    def get_total_statistics(self, obj):
        total_shows = obj.statistics.aggregate(total_shows=models.Sum("shows")).get(
            "total_shows"
        )
        total_clicks = obj.statistics.aggregate(
            total_clicks=models.Sum("clicks")
        ).get("total_clicks")
        total_spent = obj.statistics.aggregate(total_spent=models.Sum("spent")).get(
            "total_spent"
        )

        total_clicks = total_clicks if total_clicks else 0
        total_shows = total_shows if total_shows else 0
        total_spent = total_spent.__round__(2) if total_spent else 0

        return f"Shows: {total_shows}, Clicks: {total_clicks}, Spent: {total_spent}"

    get_total_statistics.short_description = "Total Statistics"


admin.site.register(Statistics, StatisticsAdmin)
admin.site.register(AdPlan, AdPlanAdmin)
admin.site.register(Report)
