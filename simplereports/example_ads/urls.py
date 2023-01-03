from django.urls import path

from . import views

app_name = 'example_ads'

urlpatterns = [
    path('', views.index, name='index'),
]
