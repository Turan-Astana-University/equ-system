import datetime
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Equipment, Cartridge, Barcode, CategoryChoices
from locations.models import Location
from users.models import User, CategoryChoicesUser
from operations.models import OperationCategoryChoices
from operations.views import create_operation_log
from django.db.models import Count
from django.contrib import messages
from django.views.generic import ListView
from inventory.mixins import AccountingRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class QRCodeView(View):

    def equipment_release_qr_scan(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            barcode_id = int(code[:-1])

            equipment = get_object_or_404(Equipment, equipment_barcode=get_object_or_404(Barcode, pk=barcode_id))
            return JsonResponse({
                'id': equipment.id,
                'name': equipment.title,
                'user': equipment.responsible.first_name,
                'message': 'Equipment found',
                'location_correct': 1,
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)

        except KeyError:
            return JsonResponse({'error': 'Location header отсутствует'}, status=400)

    def qr_cartridge_release(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            barcode_id = int(code[:-1])

            barcode = get_object_or_404(Barcode, pk=barcode_id)
            cart = get_object_or_404(Cartridge, cartridge_barcode=barcode)
            return JsonResponse({
                'id': cart.id,
                'name': cart.title,
                'user': cart.responsible.first_name,
                'message': 'Equipment found',
                'location_correct': 1,
            })
        except json.JSONDecodeError:
            messages.error(request, "Ошибка декодирования")
            return redirect("home")
        except Cartridge.DoesNotExist:
            messages.error(request, "Картридж не существует")
            return redirect("home")
        except Barcode.DoesNotExist:
            messages.error(request, "Неправильный или не существует штрихкод")
            return redirect("home")
        except Exception as e:
            messages.error(request, "Возникла ошибка")
            return redirect("home")

    def equipment_inventory_qr_scan(self, request, *args, **kwargs):
        try:
            location = get_object_or_404(Location, pk=request.headers.get('Location'))
            data = json.loads(request.body)
            code = data.get('code', '')
            barcode_id = int(code[:-1])
            equipment = get_object_or_404(Equipment, equipment_barcode=get_object_or_404(Barcode, pk=barcode_id))
            equipment.date_last_invent = datetime.datetime.now()
            equipment_true_position = location == equipment.location

            equipment.is_true_position = equipment_true_position
            if equipment_true_position:
                create_operation_log(request, operation_type=OperationCategoryChoices.INVENTORY,
                                     equipment=equipment,
                                     location_old=equipment.location,
                                     location_new=location,
                                     responsible_old=equipment.responsible,
                                     responsible_new=location.responsible)
                messages.success(request, f"{equipment.title} Успешно найдено на своей позиции")
            else:
                create_operation_log(request, operation_type=OperationCategoryChoices.MOVED_WITHOUT_NOTICE,
                                     equipment=equipment,
                                     location_old=equipment.location,
                                     location_new=location,
                                     responsible_old=equipment.responsible,
                                     responsible_new=location.responsible)
                messages.success(request, f"{equipment.title} Успешно найдено в неправильной позиции")
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
        elif request.headers.get('equipment-type') == "release_cartridge":
            return self.qr_cartridge_release(request, *args, **kwargs)
        else:
            return self.equipment_inventory_qr_scan(request, *args, **kwargs)


class ReleaseEquipmentsView(PermissionRequiredMixin, View):
    template_name = "equipments/release.html"
    permission_required = "equipments.change_equipment"
    raise_exception = False  # Отключаем исключение 403 Forbidden

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect("home")  # Перенаправляем на страницу без доступа

    def get(self, request):
        if request.user.is_anonymous:
            return redirect("login")
        result = Equipment.objects.filter(responsible=request.user)
        locations = Location.objects.all()
        users = User.objects.all()
        return render(request, self.template_name, context={
            "equipments": result,
            "locations": locations,
            "users": users,
        })

    def post(self, request):
        for i in range(len(request.POST.getlist("name[]"))):
            equipment = Equipment.objects.get(pk=request.POST.getlist("name[]")[i], responsible=request.user)
            location_old = equipment.location
            location_new = Location.objects.get(pk=request.POST.getlist("location[]")[i])
            responsible_old = equipment.responsible
            responsible_new = User.objects.get(pk=request.POST.getlist("responsible_person[]")[i])
            equipment.location = location_new
            equipment.responsible = responsible_new
            create_operation_log(request, operation_type=OperationCategoryChoices.RELEASE_EQUIPMENT, equipment=equipment,
                                 location_old=location_old, location_new=location_new,
                                 responsible_old=responsible_old,
                                 responsible_new=responsible_new)
            equipment.save()
        messages.success(request, "Операция выполнена успешно!")
        return redirect("home")


class CartridgeRelease(PermissionRequiredMixin, View):
    template_name = "equipments/cartridge_release.html"
    permission_required = "equipments.change_cartridge"
    raise_exception = False  # Отключаем исключение 403 Forbidden

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect("home")  # Перенаправляем на страницу без доступа

    def get(self, request):
        if request.user.is_anonymous:
            return redirect("login")
        cartridges = (
            Cartridge.objects.filter(responsible=request.user)
            .values("pk", 'title', 'status', 'location').filter(status__in=[CategoryChoices.NEW, CategoryChoices.FILLED])
            .annotate(count=Count('title'))
            .order_by('title')
        )
        print(cartridges)
        locations = Location.objects.all()
        users = User.objects.all()
        choices = CategoryChoices.choices
        return render(request, self.template_name, context={
            "cartridges": cartridges,
            "locations": locations,
            "users": users,
            "choices": choices,
        })

    def post(self, request):
        for i in range(len(request.POST.getlist("name[]"))):
            print(i)
            cartridge = Cartridge.objects.filter(
                title=request.POST.getlist("name[]")[i],
                status__in=[CategoryChoices.FILLED, CategoryChoices.NEW],
                responsible=request.user,
            )
            if cartridge:
                cartridge = cartridge[0]
            cartridge.status = CategoryChoices.RELEASE
            location_old = cartridge.location
            location_new = Location.objects.get(pk=request.POST.getlist("location[]")[i])
            responsible_old = cartridge.responsible
            responsible_new = User.objects.get(pk=request.POST.getlist("responsible_person[]")[i])

            user_cartridge_new = request.user
            print(user_cartridge_new)
            location_cartridge_new = Location.objects.get(pk=user_cartridge_new.pk)

            cartridge_old = Cartridge.objects.get(pk=request.POST.getlist("cartridge_old[]")[i])
            status_cartridge_old = request.POST.getlist("status[]")[i]
            cartridge_old.status = status_cartridge_old
            cartridge_old.responsible = user_cartridge_new
            cartridge_old.location = location_cartridge_new
            cartridge_old.save()
            cartridge.location = location_new
            cartridge.responsible = responsible_new
            create_operation_log(request, operation_type=OperationCategoryChoices.RELEASE_CARTRIDGE, cartridge=cartridge,
                                 cartridge_old=cartridge_old,
                                 location_old=location_old, location_new=location_new, responsible_old=responsible_old,
                                 responsible_new=responsible_new)
            cartridge.save()
        messages.success(request, "Операция выполнена успешно!")
        return redirect("home")


class MovingEquipmentsView(PermissionRequiredMixin, View):
    template_name = "equipments/moving.html"
    permission_required = (
        "equipments.add_equipment"
        "equipments.change_equipment",
        "equipments.delete_equipment",
        "equipments.view_equipment"
    )
    raise_exception = False  # Отключаем исключение 403 Forbidden

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect("home")  # Перенаправляем на страницу без доступа

    def get(self, request):
        result = Equipment.objects.all()
        locations = Location.objects.all()
        users = User.objects.all()
        return render(request, self.template_name, context={
            "equipments": result,
            "locations": locations,
            "users": users,
        })

    def post(self, request):
        for i in range(len(request.POST.getlist("name[]"))):
            equipment = Equipment.objects.get(pk=request.POST.getlist("name[]")[i])
            location_old = equipment.location
            location_new = Location.objects.get(pk=request.POST.getlist("location[]")[i])
            responsible_old = equipment.responsible
            responsible_new = User.objects.get(pk=request.POST.getlist("responsible_person[]")[i])
            equipment.location = location_new
            equipment.responsible = responsible_new
            create_operation_log(request, operation_type=OperationCategoryChoices.RELEASE_EQUIPMENT, equipment=equipment,
                                 location_old=location_old, location_new=location_new,
                                 responsible_old=responsible_old,
                                 responsible_new=responsible_new)
            equipment.save()

        return redirect("home")


class MyEquipments(ListView):
    template_name = "equipments/my_equipments_list.html"
    model = Equipment
    context_object_name = 'objects'
    paginate_by = 10

    def get_queryset(self):
        """
          Фильтруем оборудование, которое принадлежит текущему пользователю.
          Предполагается, что в модели Equipment есть поле 'responsible', которое связано с пользователем.
        """
        return Equipment.objects.filter(responsible=self.request.user)


def get_cartridges(request, *args, **kwargs):
    data = json.loads(request.body)
    location_pk = (int(data.get('location', '')))
    location = Location.objects.get(pk=location_pk)
    cartridges = Cartridge.objects.filter(location=location).values("pk", "title", "status", "responsible__first_name", "responsible__last_name")
    return JsonResponse(
        {
            'cartridges': list(cartridges)
        }
    )