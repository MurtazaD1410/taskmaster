from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcceptInvitationView,
    InvitationCreateView,
    PendingInvitationListView,
    DeclineInvitationView,
)


invitation_urlpatterns = [
    path(
        "projects/<int:project_pk>/invitations/",
        InvitationCreateView.as_view(),
        name="invitation-create",
    ),
    path(
        "invitations/accept/", AcceptInvitationView.as_view(), name="accept-invitation"
    ),
    path(
        "invitations/decline/",
        DeclineInvitationView.as_view(),
        name="reject-invitation",
    ),
    path(
        "invitations/pending/",
        PendingInvitationListView.as_view(),
        name="pending-invitations",
    ),
]

router = DefaultRouter()

urlpatterns = [
    path("", include(invitation_urlpatterns)),
]
