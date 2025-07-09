from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskOrderUpdateView

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

# The API URLs are now determined automatically by the render
urlpatterns = [
    path(
        "tasks/update-order/",
        TaskOrderUpdateView.as_view(),
        name="update_order",
    ),
    path("", include(router.urls)),
]
