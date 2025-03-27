from django.urls import path
from .views import klip_login_prepare, klip_login_request, klip_login_result

urlpatterns = [
    path("login/prepare/", klip_login_prepare, name="klip_login_prepare"),
    path("login/request/<str:request_key>/", klip_login_request, name="klip_login_request"),
    path("login/result/<str:request_key>/", klip_login_result, name="klip_login_result"),
]