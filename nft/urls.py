from django.urls import path
from . import views

urlpatterns = [
    path("mint/", views.mint_nft_api, name="mint_nft"),
    path("listNFT/", views.list_nft_api, name="list_nft"),
    path("buyNFT/", views.request_buy_nft_api, name="buy_nft"),
    path("confirmBuyNFT/", views.confirm_buy_nft, name="confirm_buy_nft"),
    path("burnNFT/", views.burn_nft, name="burn_nft"),
    path("getAllItems/", views.get_all_items, name="get_all_items"),
    path("getListedUserItem/", views.get_listed_user_item, name="get_listed_user_item"),
    path("getUserItem/", views.get_user_item, name="get_user_item"),
]
