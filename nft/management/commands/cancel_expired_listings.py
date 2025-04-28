from django.core.management.base import BaseCommand
from nft.models import Item
from datetime import datetime
from web3 import Web3
from django.conf import settings
import json
from django.utils import timezone

# Web3 초기화
w3 = Web3(Web3.HTTPProvider(settings.KLAYTN_RPC_URL))
admin_address = Web3.to_checksum_address(settings.ADMIN_ADDRESS)
admin_private_key = settings.ADMIN_PRIVATE_KEY
nft_contract_address = Web3.to_checksum_address(settings.NFT_CONTRACT_ADDRESS)

# ABI 로드
with open("abi.json") as f:
    nft_abi = json.load(f)

nft_contract = w3.eth.contract(address=nft_contract_address, abi=nft_abi)

# 트랜잭션 서명 및 전송 함수
def send_transaction(tx):
    tx.update({
        "nonce": w3.eth.get_transaction_count(admin_address),
        "gas": 3000000,
        "maxFeePerGas": w3.to_wei("25", "gwei"),
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=admin_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)

class Command(BaseCommand):
    help = "Cancel expired NFT listings"

    def handle(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())
        expired_items = Item.objects.filter(is_listed=True, listing_duration__lte=now   )

        for item in expired_items:
            try:
                # 스마트 컨트랙트 cancelListing 호출
                tx = nft_contract.functions.cancelListing(item.token_id).build_transaction({
                    "from": admin_address,
                    "nonce": w3.eth.get_transaction_count(admin_address),
                    "gas": 500000,
                    "maxFeePerGas": w3.to_wei("25", "gwei"),
                })
                tx_hash = send_transaction(tx)

                # DB에서 is_listed 업데이트
                item.is_listed = False
                item.price_klay = 0
                item.listing_duration = None
                item.save()

                self.stdout.write(f"Canceled listing for token_id: {item.token_id}, tx_hash: {tx_hash}")
            except Exception as e:
                self.stderr.write(f"Failed to cancel listing for token_id: {item.token_id}, error: {str(e)}")
