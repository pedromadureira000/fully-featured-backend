from django.urls import path
from fully_featured.user.views import (
    change_password,
    obtain_auth_token,
    sign_up,
    user_view,
)

urlpatterns = [
    path('gettoken', obtain_auth_token, name='gettoken'),
    path('user_view', user_view, name='user_view'),
    path('sign_up', sign_up, name='sign_up'),
    path('change_password', change_password, name='change_password'),
]
