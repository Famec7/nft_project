from django.urls import path
from .views import klip_prepare, klip_request, klip_result

urlpatterns = [
    path("auth/prepare/", klip_prepare, name="klip_prepare"),
    path("auth/request/<str:request_key>/", klip_request, name="klip_request"),
    path("auth/result/<str:request_key>/", klip_result, name="klip_result"),
]