from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.db import connection

def health(request):
    try:
        connection.ensure_connection()
        return JsonResponse({
            "status": "ok",
            "db": "connected"
        })
    except Exception:
        return JsonResponse({
            "status": "error",
            "db": "disconnected"
        }, status=500)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),

    # JWT endpoints
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Accounts app
    path("api/auth/", include("accounts.urls")),
    path("api/", include("catalog.urls")),
    path("api/", include("orders.urls")),
    path("api/", include("payments.urls")),

]
