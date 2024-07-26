from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
from datetime import datetime
from operations.models import Operation, OperationType
from .models import Inventory
# Create your views here.


def location_view(request):
    loc = Location.objects.all()
    return render(request, 'inventory/location_view.html', {"locations": loc})


def create_invent(request):
    new = Inventory(date_start=datetime.now())
    new.save()
    return HttpResponse(status=200)


def invent(request):
    return render(request, template_name="inventory/invent.html")


def location_detail_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    equipments = Equipment.objects.filter(location=location)
    inventory = Inventory.objects.last()
    equipments_found = equipments.filter(date_last_invent__gte=inventory.date_start)
    equipments_non_found = equipments.filter(date_last_invent__lte=inventory.date_start)
    print(equipments_non_found)
    return render(request, 'inventory/location_detail.html', {'location': location, "equipments_non_found": equipments_non_found, "equipments_found": equipments_found})


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












