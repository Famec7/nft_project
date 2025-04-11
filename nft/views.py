import json
import requests
from django.conf import settings
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics
from rest_framework.views import APIView
from .models import Item
from web3 import Web3

BAPP_NAME = settings.BAPP_NAME
KAIA_ADDRESS = settings.KAIA_ADDRESS
KLIP_PREPARE_URL = settings.KLIP_PREPARE_URL
KLIP_REQUEST_URL = settings.KLIP_REQUEST_URL
NFT_CONTRACT_ADDRESS = settings.NFT_CONTRACT_ADDRESS

# 스마트 컨트랙트 실행
def execute_contract(txTo, functionJSON, value, params):
    payload = {
        "bapp": {"name": BAPP_NAME},
        "type": "execute_contract",
        "transaction": {
            "to": txTo,
            "value": value,
            "abi": functionJSON,
            "params": params,
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(KLIP_PREPARE_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # 성공 시 Klip 응답 반환
    else:
        return {"error": response.text}  # 실패 시 에러 반환
    
# NFT 발행 API
@csrf_exempt
def mint_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            toAddress = body.get("toAddress")
            tokenID = body.get("tokenID")
            uri = body.get("uri")
            
            if not toAddress or not tokenID or not uri:
                return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
            result = mint_nft(toAddress, tokenID, uri)
            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def mint_nft(toAddress, tokenID, uri):
    functionJSON = json.dumps({
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"},
            {"name": "tokenURI", "type": "string"}
        ],
        "name": "mintWithTokenURI",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    })
    functionParams = json.dumps([toAddress, tokenID, uri])
    value = "0"
    
    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)

# NFT 마켓 등록 API
@csrf_exempt
def list_nft_api(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            token_id = int(body.get("token_id"))
            price_klay = float(body.get("price_klay"))
            price_wei = str(Web3.to_wei(price_klay, 'ether'))

            result = list_nft(token_id, price_wei)
            
            item = Item.objects.create(
                token_id=token_id,
                seller=KAIA_ADDRESS,
                price_klay=price_klay,
                is_listed=True,
                metadata_uri="https://example.com/metadata/" + str(token_id) + ".json"
            )
            item.save()
            
            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

def list_nft(token_id, price_wei):
    functionJSON = json.dumps({
        "constant": False,
        "inputs": [
            {"name": "tokenId", "type": "uint256"},
            {"name": "price", "type": "uint256"},
        ],
        "name": "listItem",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    })

    functionParams = json.dumps([token_id, price_wei])
    value = "0"

    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)

# NFT 구입 API
@csrf_exempt
def buy_nft_api(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            token_id = int(body.get("token_id"))
            price_klay = float(body.get("price_klay"))
            price_wei = Web3.to_wei(price_klay, 'ether')

            result = buy_nft(token_id, price_wei)
            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

def buy_nft(tokenID, price_wei):
    functionJSON = json.dumps({
        "constant": False,
        "inputs": [
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "buy",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    })
    
    functionParams = json.dumps([tokenID])
    value = str(price_wei)

    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)