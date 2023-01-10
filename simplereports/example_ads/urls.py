from django.urls import include, path

from . import views


app_name = 'example_ads'

urlpatterns = [
    path('report/', views.index3, name='index3'),
    path('', views.index2, name='index2'),
    path('demo/', views.index, name='index'),
    path('api/', include('example_api.urls', namespace='api')),
]
