from django.urls import include, path

from . import views


app_name = 'example_ads'

urlpatterns = [
    path('report/', views.report, name='report'),
    path('', views.constructor, name='constructor'),
    path('about', views.about, name='about'),
    path('demo/', views.index, name='index'),
]
