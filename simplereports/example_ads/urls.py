from django.urls import path

from . import views

app_name = 'example_ads'

urlpatterns = [
    path('report/', views.index3, name='index3'),
    path('', views.index2, name='index2'),
]
