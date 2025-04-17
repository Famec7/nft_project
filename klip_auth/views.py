import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

KLIP_PREPARE_URL = settings.KLIP_PREPARE_URL
KLIP_REQUEST_URL = settings.KLIP_REQUEST_URL
KLIP_RESULT_URL = settings.KLIP_RESULT_URL

# Klip API 요청 (request_key 생성)
@csrf_exempt
def klip_prepare(request):
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

# Klip 딥링크 생성
@csrf_exempt
def klip_request(request, request_key):
    if request.method == "GET":
        return JsonResponse({"url": KLIP_REQUEST_URL + request_key})
    
    return JsonResponse({"error": "Failed to request Klip login"}, status=400, allow_redirects=True)

# Klip 결과 확인
@csrf_exempt
def klip_result(request, request_key):
    if request.method == "GET":
        headers = {"Content-Type": "application/json"}
        response = requests.get(KLIP_RESULT_URL + request_key, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, status=200)
        
    return JsonResponse({"error": "Failed to get Klip login result"}, status=400)