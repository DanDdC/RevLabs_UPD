"""
URL configuration for project project.
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from revlabs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.RevLabsLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('circuits/', views.track_selection, name='track_selection'),
    path('vehicles/', views.car_selection, name='car_selection'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/laps/', views.api_telemetry_laps, name='api_telemetry_laps'),
    path('api/import-telemetry/', views.api_import_telemetry, name='api_import_telemetry'),
]
