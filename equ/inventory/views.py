from django.http import HttpResponse
from django.shortcuts import render
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
from datetime import datetime
from operations.models import Operation
# Create your views here.


def location_view(request):
    loc = Location.objects.all()
    print(loc)
    return render(request, 'inventory/location_view.html', {"locations": loc})


def location_detail_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    equipments = Equipment.objects.filter(location=location)
    print(equipments)
    return render(request, 'inventory/location_detail.html', {'location': location, "equipments": equipments})


def equ_invent_find(request):
    if request.method == "POST":
        equipment_id = request.POST.get('equipment_id')
        equ = Equipment.objects.get(id=equipment_id)
        location = Location.objects.get(id=request.POST.get('location_id'))

        if equ.location != location:
            print('НЕ СОВПАДЕНИЕ')
            return HttpResponse(status=200)
        equ.date_last_invent = datetime.now()
        equ.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)












