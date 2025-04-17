import requests
from django.conf import settings

BAPP_NAME = settings.BAPP_NAME
KLIP_PREPARE_URL = settings.KLIP_PREPARE_URL

# Klip Execute_contract 함수
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
    
def send_token(fromAddress, toAddress, amount):
    payload = {
        "bapp": {"name": BAPP_NAME},
        "chain": "klaytn",
        "type": "send_token",
        "transaction": {
            "contract": "0x0000000000000000000000000000000000000000",
            "from": fromAddress,
            "to": toAddress,
            "amount": amount,
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(KLIP_PREPARE_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # 성공 시 Klip 응답 반환
    else:
        return {"error": response.text}  # 실패 시 에러 반환