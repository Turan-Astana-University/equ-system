import datetime
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from locations.models import Location
from operations.views import create_operation_log
from .models import Equipment
from locations.models import Location
from users.models import User
from inventory.mixins import SuperuserRequiredMixin
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
        name_pks = request.POST.getlist('name[]')
        name_pks = list(map(int, name_pks))
        equipments = Equipment.objects.filter(pk__in=name_pks)

        # Здесь вы можете добавить логику для обработки освобождения оборудования, например:
        # for equipment in equipments:
        #     equipment.release()  # Пример метода освобождения оборудования

        print(equipments)  # Вывод для отладки
        return redirect("home")