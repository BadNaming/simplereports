from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ReportViewSet,
    StatisticsViewSet,
    download_report,
    add_daily_data,
    create_report_for_the_period,
)

router_v1 = DefaultRouter()
router_v1.register("my_reports", ReportViewSet, basename="my_reports")
router_v1.register("statistics", StatisticsViewSet, basename="statistics")


urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("v1/report/download/<int:pk>/", download_report, name="download_report"),
    path("v1/add_daily_data/", add_daily_data, name="get_daily_report"),
    path(
        "v1/create_report/",
        create_report_for_the_period,
        name="create_report_for_the_period",
    ),
]
