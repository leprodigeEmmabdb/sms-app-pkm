"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path

from sms import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('sms/', include('sms.sms_urls.py')),
    # path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('sms/', views.send_sms, name='send_sms'),
    path('sms/historique/', views.history, name='history'),
    path('contacts/', views.contact, name='contact'),
    path('settings/', views.settings, name='settings'),
    path('send_sms/', views.send_sms_view, name='send_sms_view'),


]
