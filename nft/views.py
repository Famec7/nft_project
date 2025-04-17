import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from decimal import Decimal
from .models import Item
from django.conf import settings
from klip.klip import send_token

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
            item_id = int(body["itemID"])
            uri = body["uri"]

            tx = nft_contract.functions.mintWithTokenURI(to, uri).build_transaction({
                "from": admin_address,
                "value": 0,
                "nonce": w3.eth.get_transaction_count(admin_address),
                "gas": 500000,
            })

            tx_hash = send_transaction(tx)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            token_id = None  # Initialize token_id with a default value
            log = tx_receipt.logs[1]

            data = log['data']
            token_id = int.from_bytes(data[2:], byteorder='big')
            
            if token_id is None:  # Handle case where token_id is not assigned
                return JsonResponse({"success": False, "error": "Minted event not found in transaction logs."})
                        
            item = Item.objects.create(
                    token_id=token_id,
                    item_id=item_id,
                    seller=admin_address,
                    price_klay=0,
                    metadata_uri=uri
                )
            item.save()
            
            return JsonResponse({"success": True, "tx_hash": tx_hash, "item": item.to_dict()})

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
            seller = Web3.to_checksum_address(body["sellerAddress"])

            price_wei = Web3.to_wei(price_klay, "ether")

            # DB에 아이템이 있는지 확인
            item = Item.objects.get(token_id=token_id)
            if not item:
                return JsonResponse({"success": False, "error": "Item not found."})
            
            item.price_klay = price_klay
            item.is_listed = True
            item.save()

            # 스마트 컨트랙트 호출
            tx = nft_contract.functions.listItem(token_id, int(price_wei), item.metadata_uri, seller).build_transaction({
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
def request_buy_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            token_id = int(body["tokenID"])
            buyer = Web3.to_checksum_address(body["buyerAddress"])
            
            item = Item.objects.get(token_id=token_id)
            if not item or not item.is_listed:
                return JsonResponse({"success": False, "error": "Item not found or not listed."})
            
            result = send_token(buyer, item.seller, str(item.price_klay))
            if "error" in result:
                return JsonResponse({"success": False, "error": result["error"]})
            else:
                result["token_id"] = token_id
                result["buyer_address"] = buyer
                return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def confirm_buy_nft(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            request_key = body["requestKey"]
            result = requests.get(settings.KLIP_RESULT_URL + request_key).json()
            
            data = result.get("result")
            
            if data.get("status") == "success":
                token_id = int(body["result"]["token_id"])
                buyer_address = Web3.to_checksum_address(body["result"]["buyer_address"])
                
                tx = buy_nft(token_id, buyer_address)
                
                item = Item.objects.get(token_id=token_id)
                item.is_listed = False
                item.save()

                return JsonResponse({"success": True, "result": result})
            else:
                return JsonResponse({"success": False, "error": "Transaction not completed." + result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        
    return JsonResponse({"success": False, "error": "Invalid request method."})
    
def buy_nft(token_id, buyer_address):
    tx = nft_contract.functions.buy(token_id, buyer_address).build_transaction({
                "from": admin_address,
                "nonce": w3.eth.get_transaction_count(admin_address),
                "gas": 500000,
                "maxFeePerGas": w3.to_wei("25", "gwei")
            })

    tx_hash = send_transaction(tx)
    
    return tx_hash

# NFT 삭제
@csrf_exempt
def burn_nft(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            token_id = int(body["tokenID"])

            # DB에서 아이템 삭제
            item = Item.objects.get(token_id=token_id)
            if not item:
                return JsonResponse({"success": False, "error": "Item not found."})

            # 스마트 컨트랙트 호출
            tx = nft_contract.functions.burn(token_id).build_transaction({
                "from": admin_address,
                "nonce": w3.eth.get_transaction_count(admin_address),
                "gas": 500000,
                "maxFeePerGas": w3.to_wei("25", "gwei")
            })

            tx_hash = send_transaction(tx)
            item.delete()

            return JsonResponse({"success": True, "tx_hash": tx_hash})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        
# NFT 마켓 전체 정보 조회
@csrf_exempt
def get_all_items(request):
    if request.method == 'GET':
        try:
            items = Item.objects.filter(is_listed=True)
            item_list = []
            for item in items:
                item_list.append({
                    "token_id": item.token_id,
                    "item_id": item.item_id,
                    "seller": item.seller,
                    "price_klay": str(item.price_klay),
                    "metadata_uri": item.metadata_uri,
                    "is_listed": item.is_listed
                })
            return JsonResponse({"success": True, "items": item_list})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        
# NFT 마켓 특정 유저 정보 조회
@csrf_exempt
def get_user_items(request):
    if request.method == 'GET':
        try:
            body = json.loads(request.body)
            user_address = Web3.to_checksum_address(body["userAddress"])
            items = Item.objects.filter(seller=user_address, is_listed=True)
            item_list = []
            for item in items:
                item_list.append({
                    "token_id": item.token_id,
                    "item_id": item.item_id,
                    "seller": item.seller,
                    "price_klay": str(item.price_klay),
                    "metadata_uri": item.metadata_uri,
                    "is_listed": item.is_listed
                })
            return JsonResponse({"success": True, "items": item_list})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})