from django.urls import path
from routes.views import RouteAPIView, health_check

urlpatterns = [
    path("api/optimize-route/", RouteAPIView.as_view()),
    path('api/health/', health_check, name='health'),
]
