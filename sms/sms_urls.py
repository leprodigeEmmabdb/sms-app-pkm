from django.urls import path, include

from rest_framework_nested import routers
from sms import views # type: ignore

router = routers.DefaultRouter()

router.register('sms', views.home, basename="sms")
# router.register('clients', ClientViewSet, basename="clients")
# router.register('audiences', AudienceViewSet, basename="audiences")
#


urlpatterns = [
    path('', include(router.urls)), 
    
]
