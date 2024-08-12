from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
from datetime import datetime
from operations.models import Operation, OperationType
from .models import Inventory
# Create your views here.


def location_view(request):
    if not Inventory.objects.last().date_end:
        loc = Location.objects.all()
        return render(request, 'inventory/locations_view.html', {"locations": loc})
    return render(request, "inventory/invent.html")


def create_invent(request):
    if request.is_superuser:
        new = Inventory(date_start=datetime.now())
        new.save()
        return redirect("locations")
        # return render(request, "inventory/invent.html")
    else:
        return HttpResponse("НЕТ ДОСТУПА")


def end_invent(request):
    inventory = Inventory.objects.last()
    if inventory.date_end:
        return HttpResponse(status=400)
    inventory.date_end = datetime.now()
    inventory.save()
    equ = Equipment.objects.all().filter(is_true_position=False).update(is_true_position=True)
    return HttpResponse(status=200)


def invent(request):
    return render(request, template_name="inventory/inventory.html")


def location_detail_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    equipments = Equipment.objects.filter(location=location)
    equipments_true = equipments.filter(is_true_position=True)
    equipments_false = equipments.filter(is_true_position=False)
    inventory = Inventory.objects.last()

    equipment_non_date_last_invent = equipments.filter(date_last_invent__isnull=True)
    print(equipment_non_date_last_invent)
    equipments_found = equipments_true.filter(date_last_invent__gte=inventory.date_start)
    equipments_non_found = equipments_true.filter(date_last_invent__lte=inventory.date_start).union(equipment_non_date_last_invent)
    return render(request, 'inventory/location_detail.html', {'location': location, "equipments_non_found": equipments_non_found, "equipments_found": equipments_found, "equipments_false": equipments_false})


def equ_invent_find(request):
    if request.method == "POST":
        equipment_id = request.POST.get('equipment_id')
        equ = Equipment.objects.get(id=equipment_id)
        location = Location.objects.get(id=request.POST.get('location_id'))

        if equ.location != location:
            Operation(date=datetime.now(), operation_type=OperationType.objects.get(pk=1), user=request.user, equipment=equ, location_old=equ.location, location_new=location, responsible_old=equ.responsible,
                      responsible_new=location.responsible).save()
            equ.location = location
            equ.responsible = location.responsible
            equ.is_true_position = False
            equ.save()
            return JsonResponse({
                'message': 'Equipment found',
                'equipment': equ.title,
                'location_correct': False
            })

        equ.date_last_invent = datetime.now()
        equ.save()
        return JsonResponse({
            'message': 'Equipment found',
            'location_correct': True
        })
    return HttpResponse(status=400)












