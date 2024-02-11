from django.urls import path
from fully_featured.user.views import (
    obtain_auth_token,
    sign_in,
    user_view
)

urlpatterns = [
    path('gettoken', obtain_auth_token, name='gettoken'),
    path('user_view', user_view, name='user_view'),
    path('sign_in', sign_in, name='sign_in'),
]
