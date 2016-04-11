from rest_framework import routers
from .views import (InnAccUserViewSet,
	TransactionView)
from django.conf.urls import url

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'innaccuser',InnAccUserViewSet)

urlpatterns = [
	url(r'transaction$', TransactionView.as_view()),
]

urlpatterns += router.urls