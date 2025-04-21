from django.shortcuts import get_object_or_404, redirect
from locations.models import Location
import json
import datetime
from operations.views import create_operation_log
from django.contrib import messages
from operations.models import OperationCategoryChoices
from django.http import JsonResponse


def update_equipment(request, *args, **kwargs):
    from equipments.models import Equipment, Barcode, Cartridge
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
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)

    except KeyError:
        return JsonResponse({'error': 'Location header отсутствует'}, status=400)


def equipment_release_qr_scan(self, request, *args, **kwargs):
    from equipments.models import Equipment, Barcode, Cartridge

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
    from equipments.models import Equipment, Barcode, Cartridge
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

def inventory_scan(request, *args, **kwargs):
    from equipments.models import Equipment, Barcode
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

