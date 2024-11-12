import datetime
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from locations.models import Location
from .models import Equipment
from locations.models import Location
from users.models import User
from operations.views import create_operation_log
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class QRCodeView(View):
    def equipment_release_qr_scan(self, request, *args, **kwargs):
        print(request.headers.get('equipment-type'))
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            product_id = int(code[:-1])
            equipment = get_object_or_404(Equipment, pk=product_id)
            print(code)

            return JsonResponse({
                'id': equipment.id,
                'name': equipment.title,
                'user': equipment.responsible.email,
                'message': 'Equipment found',
                'location_correct': 1,
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)

        except KeyError:
            return JsonResponse({'error': 'Location header отсутствует'}, status=400)

    def equipment_inventory_qr_scan(self, request, *args, **kwargs):
        try:
            location = get_object_or_404(Location, pk=request.headers.get('Location'))
            data = json.loads(request.body)
            code = data.get('code', '')
            product_id = int(code[:-1])
            equipment = get_object_or_404(Equipment, pk=product_id)
            equipment.date_last_invent = datetime.datetime.now()
            equipment_true_position = location == equipment.location

            equipment.is_true_position = equipment_true_position
            if equipment_true_position:
                create_operation_log(request, operation_type=1,
                                     equipment=equipment,
                                     location_old=equipment.location,
                                     location_new=location,
                                     responsible_old=equipment.responsible,
                                     responsible_new=location.responsible)
            else:
                create_operation_log(request, operation_type=3,
                                     equipment=equipment,
                                     location_old=equipment.location,
                                     location_new=location,
                                     responsible_old=equipment.responsible,
                                     responsible_new=location.responsible)
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

    def post(self, request, *args, **kwargs):
        if request.headers.get('equipment-type') == "release":
            return self.equipment_release_qr_scan(request, *args, **kwargs)
        else:
            return self.equipment_inventory_qr_scan(request, *args, **kwargs)


class ReleaseEquipmentsView(View):
    template_name = "equipments/release.html"

    def get(self, request):
        if request.user.is_anonymous:
            return redirect("login")
        # Получение оборудования, которое в ответе, местонахождений и пользователей
        result = Equipment.objects.filter(responsible=request.user)
        locations = Location.objects.all()
        users = User.objects.all()
        return render(request, self.template_name, context={
            "equipments": result,
            "locations": locations,
            "users": users,
        })

    def post(self, request):
        # Обработка POST-запроса для освобождения оборудования
        print(request.POST.getlist("name[]"))
        for i in range(len(request.POST.getlist("name[]"))):
            equipment = Equipment.objects.get(pk=request.POST.getlist("name[]")[i])
            print(equipment)
            location_old = equipment.location
            print(location_old)
            location_new = Location.objects.get(pk=request.POST.getlist("location[]")[i])
            print(request.POST.getlist("location[]"))
            print(location_new)
            responsible_old = equipment.responsible
            responsible_new = User.objects.get(pk=request.POST.getlist("responsible_person[]")[i])
            equipment.location = location_new
            equipment.responsible = responsible_new
            create_operation_log(request, 2, equipment, location_old, location_new, responsible_old, responsible_new)
            equipment.save()

        return redirect("home")