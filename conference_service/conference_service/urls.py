"""
URL configuration for conference_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('conferences/', ConferenceListView.as_view(), name='conference-list'),
    path('conference/create/', ConferenceCreateView.as_view(), name='conference-create'),
    path('conference/detail/', ConferenceDetailView.as_view(), name='conference-detail'),
    path('conference/approve_reject/', ApproveRejectConferenceView.as_view(), name='approve-reject-conference'),
    path('conference/update-status/', ConferenceStatusUpdateView.as_view(), name='conference-update-status'),
    path('invitation-status/', InvitationStatusAPIView.as_view(), name='invitation-status'),
    path('invitation/create/', InvitationCreateView.as_view(), name='invitation-create'),
    path('invitation/show/', UserInvitationsAPIView.as_view(), name='user-invitations'),
    path('invitation/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('invitation/reject/', RejectInvitationView.as_view(), name='reject-invitation'),
]
