"""
URL configuration for paper_service project.

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
    path('papers/', PaperListView.as_view(), name='paper-list'),
    path('paper/submit/', PaperSubmissionView.as_view(), name='paper-submit'),
    path('my_submissions/', MySubmissionsView.as_view(), name='my_submissions_api'),
    path('my_submissions/update/', MySubmissionUpdateView.as_view(), name='my_submissions_update_api'),
    path('update_paper/<int:paper_id>/', UpdatePaperView.as_view(), name='update-paper'),
    path('update_paper/conference/<int:conference_id>/', UpdatePaperConferenceView.as_view(), name='update-paper-conference'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', NewReviewsView.as_view(), name='reviews-create'),
    path('reviews/show/', MyReviewsView.as_view(), name='reviews-show'),
    path('reviews/check-statues/<int:conferenceId>/', CheckReviewsView.as_view(), name='reviews-show'),
    path('reviews/update/', UpdateReviewAPI.as_view(), name='reviews-update'),
    path('reviews/rebuttal/<int:paper_id>/', RebuttalView.as_view(), name='rebuttal'),
    path('reviews/update-rebuttal/<int:paper_id>/<int:reviewer_id>/', UpdateRebuttalView.as_view(), name='update-rebuttal'),
        

]
