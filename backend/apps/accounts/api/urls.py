from django.urls import path
from apps.accounts.api.token_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)
from apps.accounts.api.views import (
    ChangePasswordAPIView,
    CurrentUserAPIView,
    LogoutAPIView,
)


app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        CustomTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "verify/",
        CustomTokenVerifyView.as_view(),
        name="token-verify",
    ),
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        CurrentUserAPIView.as_view(),
        name="current-user",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
]