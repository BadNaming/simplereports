from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import callback, get_info, ReportTaskViewset

router_v1 = DefaultRouter()
router_v1.register(r'report_task', ReportTaskViewset)


urlpatterns = [
    path('v1/info/', get_info, name='get_info'),
    path('v1/vk/', callback, manage='callback'),
    path('v1/', include(router_v1.urls)),
]