from django.urls import path
from .views import mint_nft_api, list_nft
from . import views

urlpatterns = [
    path("mint/", mint_nft_api, name="mint_nft"),
    path("listNFT/", list_nft, name="list_nft"),
]
