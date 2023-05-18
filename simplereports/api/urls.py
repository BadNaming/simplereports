from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReportTaskViewset, callback, get_info

router_v1 = DefaultRouter()
router_v1.register(r'report_task', ReportTaskViewset)


urlpatterns = [
    path('v1/info/', get_info, name='get_info'),
    path('v1/vk/', callback, name='callback'),
    path('v1/', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))]
