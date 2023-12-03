"""
URL configuration for frontend_service project.

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
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', views.admin, name='admin'),
    path('', views.index, name='main'),
    path('login/', views.login, name='login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('home/', views.home, name='home'),
    path('submit/', views.paper_submit, name='submit'),
    path('invitation/', views.invitation, name='invite'),
    path('my_review/', views.my_review, name='review'),
    path('rebuttal/', views.rebuttal, name='rebuttal'),
    path('start_review/', views.my_review_start_submit, name='start-review'),
    path('register/', views.register, name='register'),
    path('login_check/', views.login_check, name='login_check'),
    path('logout/', views.logout, name='logout'),
    path('create_conference/', views.create_conference, name='conference-create'),
    path('conference/approve_reject/', views.approve_reject_conference, name='approve-reject-conference'),

]
