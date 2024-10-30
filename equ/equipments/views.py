import datetime
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from locations.models import Location
from operations.views import create_operation_log
from .models import Equipment
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class QRCodeView(View):
    def post(self, request, *args, **kwargs):
        try:
            location = get_object_or_404(Location, pk=request.headers.get('Location'))
            data = json.loads(request.body)
            code = data.get('code', '')
            product_id = int(code[:-1])
            equipment = get_object_or_404(Equipment, pk=product_id)
            equipment.date_last_invent = datetime.datetime.now()
            equipment_true_position = location == equipment.location

            equipment.is_true_position = equipment_true_position
            create_operation_log(request, operation_type=1,
                                 equipment=equipment,
                                 location_old=equipment.location,
                                 location_new=location,
                                 responsible_old=equipment.responsible,
                                 responsible_new=location.responsible)
            if not equipment_true_position:
                equipment.location = location
            equipment.save()

            return JsonResponse({
                'id': equipment.id,
                'name': equipment.title,
                'user': equipment.responsible.email,
                'message': 'Equipment found',
                'location_correct': equipment_true_position
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Location header отсутствует'}, status=400)


def release_equipments(request):
    return render(request, template_name="equipments/release.html")