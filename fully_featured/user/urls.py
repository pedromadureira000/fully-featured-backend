from django.urls import path
from fully_featured.user.views import (
    obtain_auth_token
)

urlpatterns = [
    path('gettoken', obtain_auth_token, name='gettoken'),
]
