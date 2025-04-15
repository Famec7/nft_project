from django.urls import path
from .views import mint_nft_api, list_nft_api, buy_nft_api, burn_nft, get_all_items, get_user_items
from . import views

urlpatterns = [
    path("mint/", mint_nft_api, name="mint_nft"),
    path("listNFT/", list_nft_api, name="list_nft"),
    path("buyNFT/", buy_nft_api, name="buy_nft"),
    path("burnNFT/", burn_nft, name="burn_nft"),
    path("getAllItems/", get_all_items, name="get_all_items"),
    path("getUserItems/", get_user_items, name="get_user_items"),
]
