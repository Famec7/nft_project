import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from decimal import Decimal
from .models import Item
from django.conf import settings

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

# NFT 민팅
@csrf_exempt
def mint_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            to = Web3.to_checksum_address(body["toAddress"])
            token_id = int(body["tokenID"])
            uri = body["uri"]

            tx = nft_contract.functions.mintWithTokenURI(to, token_id, uri).build_transaction({
                "from": admin_address,
                "value": 0,
            })

            tx_hash = send_transaction(tx)
            
            item = Item.objects.create(
                    token_id=token_id,
                    seller=admin_address,
                    price_klay=0,
                    metadata_uri=uri
                )
            item.save()
            
            return JsonResponse({"success": True, "tx_hash": tx_hash})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

# NFT 마켓에 등록
@csrf_exempt
def list_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            token_id = int(body["tokenID"])
            price_klay = Decimal(body["price"])

            price_wei = Web3.to_wei(price_klay, "ether")

            # DB에 아이템이 있는지 확인
            item = Item.objects.get(token_id=token_id)
            if not item:
                return JsonResponse({"success": False, "error": "Item not found."})
            
            item.price_klay = price_klay
            item.is_listed = True
            item.save()

            # 스마트 컨트랙트 호출
            tx = nft_contract.functions.listItem(token_id, int(price_wei), item.metadata_uri).build_transaction({
                "from": admin_address,
                "nonce": w3.eth.get_transaction_count(admin_address),
                "gas": 500000,
                "maxFeePerGas": w3.to_wei("25", "gwei")
            })

            tx_hash = send_transaction(tx)

            return JsonResponse({"success": True, "tx_hash": tx_hash})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
# NFT 구매
@csrf_exempt
def buy_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            token_id = int(body["tokenID"])
            price_klay = Decimal(body["price"])
            price_wei = Web3.to_wei(price_klay, "ether")

            tx = nft_contract.functions.buy(token_id).build_transaction({
                "from": admin_address,
                "value": int(price_wei),
            })

            tx_hash = send_transaction(tx)
            return JsonResponse({"success": True, "tx_hash": tx_hash})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
