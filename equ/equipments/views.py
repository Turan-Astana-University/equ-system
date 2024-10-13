import datetime
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from locations.models import Location
from .models import Equipment


@method_decorator(csrf_exempt, name='dispatch')
class QRCodeView(View):
    def post(self, request, *args, **kwargs):
        try:
            location = get_object_or_404(Location, pk=request.headers.get('Location'))
            data = json.loads(request.body)
            code = data.get('code', '')
            # Здесь можно добавить логику обработки полученного QR-кода.
            print(code)
            product_id = int(code[:-1])
            equipment = get_object_or_404(Equipment, pk=product_id)
            equipment.date_last_invent = datetime.datetime.now()
            equipment.save()
            print(equipment)
            print('Получен QR-код:', code)

            return JsonResponse({
                'id': equipment.id,
                'name': equipment.title,
                'user': equipment.responsible.email,
                'message': 'Equipment found',
                'location_correct': location == equipment.location
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Location header отсутствует'}, status=400)

        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
#
# @csrf_exempt
# def qr_code_view(request):
#     if request.method == 'POST':
#         try:
#             location = Location.objects.get(pk=request.headers['Location'])
#             data = json.loads(request.body)
#             code = data.get('code', '')
#             # Здесь можно добавить логику обработки полученного QR-кода.
#             print(code)
#             product_id = int(code[:-1])
#             equipment = get_object_or_404(Equipment, pk=product_id)
#             equipment.date_last_invent= datetime.datetime.now()
#             equipment.save()
#             print(equipment)
#             print('Получен QR-код:', code)
#             return JsonResponse({
#                 'id': equipment.id,
#                 'name': equipment.title,
#                 'user': equipment.responsible.email,
#                 'message': 'Equipment found',
#                 'location_correct': location == equipment.location
#             })
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
#     return JsonResponse({'error': 'Метод не поддерживается'}, status=405)