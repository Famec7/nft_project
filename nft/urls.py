from django.urls import path
from .views import mint_nft_api, list_nft_api
from . import views

urlpatterns = [
    path("mint/", mint_nft_api, name="mint_nft"),
    path("listNFT/", list_nft_api, name="list_nft"),
]
