import json
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .models import NFTItem
from .serializers import NFTItemSerializer

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
    response = requests.post(KLIP_PREPARE_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        return response.json()  # 성공 시 Klip 응답 반환
    else:
        return {"error": response.text}  # 실패 시 에러 반환
    
# NFT 발행 API
def mint_nft(toAddress, tokenID, uri):
    functionJSON = '[{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"},{"name":"tokenURI","type":"string"}],"name":"mintWithTokenURI","outputs":[{"name":"", "type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    functionParams = [toAddress, tokenID, uri]
    value = "0"
    
    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)

# NFT 마켓 등록 API
def list_nft(tokenID, price):
    functionJSON = '[{"constant":true,"inputs":[{"name":"tokenId","type":"uint256"}, {"name":"price","type":"uint256"}],"name":"listItem","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    functionParams = [tokenID, price]
    value = "0"
    
    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)

# NFT 구매 API
def buy_nft(fromAddress, tokenID):
    functionJSON = '[{"constant":true,"inputs":[{"name":"from","type":"address"},{"name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    functionParams = [fromAddress, tokenID]
    value = "0"
    
    return execute_contract(NFT_CONTRACT_ADDRESS, functionJSON, value, functionParams)