from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ReportViewSet,
    download_report,
    add_daily_data,
    get_report,
    create_report_for_the_period,
)

router_v1 = DefaultRouter()
router_v1.register("my_reports", ReportViewSet, basename="my_reports")


urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("v1/report/", get_report, name="get_report"),
    path("v1/report/download/<int:pk>/", download_report, name="download_report"),
    path("v1/add_daily_data/", add_daily_data, name="get_daily_report"),
    path(
        "v1/create_report/",
        create_report_for_the_period,
        name="create_report_for_the_period",
    ),
]
