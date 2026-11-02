"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import include, path

from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('relation/', views.relation, name='relation'),
    path('questions/', views.questions, name='questions'),
    path('login/', views.LearningLoginView.as_view(), name='account_login'),
    path('signup/', views.learning_signup, name='account_signup'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='account_logout',
    ),
    path('shop/', include(('home.urls', 'shop'), namespace='shop')),
]
