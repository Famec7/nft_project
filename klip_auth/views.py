import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

KLIP_PREPARE_URL = 'https://a2a-api.klipwallet.com/v2/a2a/prepare'
KLIP_REQUEST_URL = 'https://klipwallet.com?target=/a2a?request_key='
KLIP_RESULT_URL = 'https://a2a-api.klipwallet.com/v2/a2a/result?request_key='

# Klip API 요청 (request_key 생성)
@csrf_exempt
def klip_login_prepare(request):
  if request.method == "POST":
        payload = {
            "bapp": {"name": "VRNFT"},
            "type": "auth"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(KLIP_PREPARE_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({"request_key": data["request_key"], "success": True})
          
  return JsonResponse({"error": "Failed to prepare Klip login"}, status=400)

# Klip 로그인 요청
@csrf_exempt
def klip_login_request(request, request_key):
    if request.method == "GET":
        return JsonResponse({"url": KLIP_REQUEST_URL + request_key})
    
    return JsonResponse({"error": "Failed to request Klip login"}, status=400)

# Klip 로그인 결과 확인
@csrf_exempt
def klip_login_result(request, request_key):
    if request.method == "GET":
        headers = {"Content-Type": "application/json"}
        response = requests.get(KLIP_RESULT_URL + request_key, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, status=200)
        
    return JsonResponse({"error": "Failed to get Klip login result"}, status=400)