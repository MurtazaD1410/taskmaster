from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    ProjectMemberRemoveView,
    ProjectMemberLeave,
    ProjectMembersList,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "projects/<int:project_pk>/members/<int:user_pk>/",
        ProjectMemberRemoveView.as_view(),
        name="project-member-remove",
    ),
    path(
        "projects/<int:project_pk>/leave/",
        ProjectMemberLeave.as_view(),
        name="project-member-leave",
    ),
    path(
        "projects/<int:project_pk>/members/",
        ProjectMembersList.as_view(),
        name="project-member-list",
    ),
]
