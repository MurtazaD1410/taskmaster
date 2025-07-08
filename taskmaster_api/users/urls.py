from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RegisterView,
    EmailLoginView,
    CurrentUserView,
    UpdateUserView,
    CheckEmailView,
)
from rest_framework_simplejwt.views import TokenRefreshView

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me", CurrentUserView.as_view(), name="current_user"),
    path("profile/", UpdateUserView.as_view(), name="update_user"),
    path("users/check-email/", CheckEmailView.as_view(), name="check-email"),
]

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("", include(router.urls)),
]
