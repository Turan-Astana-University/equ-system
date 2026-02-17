import requests
from django.http import JsonResponse
from django.conf import settings


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_print_request(request, zpl_code):
    if request.method == "GET":
        client_ip = get_client_ip(request)

        if not zpl_code:
            return JsonResponse({"error": "Не указан zpl_data"}, status=400)

        fastapi_url = getattr(settings, "PRINT_SERVICE_URL", "http://192.168.115.165:8563/print")

        try:
            response = requests.post(
                fastapi_url,
                json={"zpl_data": zpl_code},
                timeout=getattr(settings, "PRINT_SERVICE_TIMEOUT", 10),
            )
            if response:
                print("YES")
            else:
                return JsonResponse(response.json(), status=response.status_code)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Не удалось подключиться к {fastapi_url}", "details": str(e)}, status=500)

    return JsonResponse({"error": "Используйте GET-запрос"}, status=405)
