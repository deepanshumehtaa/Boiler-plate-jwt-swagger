from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet
from quotes.views import QuoteViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'quotes', QuoteViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
