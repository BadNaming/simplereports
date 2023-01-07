from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('example_ads.urls', namespace='ads')),
    path('api/', include('example_api.urls', namespace='api')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
]
