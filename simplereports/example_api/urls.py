from django.urls import path

from . import views

app_name = 'example_api'

urlpatterns = [
    path('', views.callback, name='callback'),
]
