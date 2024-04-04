from django.urls import path
from fully_featured.user.views import (
    change_password,
    obtain_auth_token,
    sign_up,
    user_view,
    reset_password_email,
    get_or_create_account_with_google
)

urlpatterns = [
    path('gettoken', obtain_auth_token, name='gettoken'),
    path('user_view', user_view, name='user_view'),
    path('sign_up', sign_up, name='sign_up'),
    path('change_password', change_password, name='change_password'),
    path('reset_password_email', reset_password_email, name='reset_password_email'),
    path('get_or_create_account_with_google', get_or_create_account_with_google, name='get_or_create_account_with_google'),
]
