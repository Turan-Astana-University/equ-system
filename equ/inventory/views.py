from django.shortcuts import render
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
# Create your views here.


def location_view(request):
    loc = Location.objects.all()
    print(loc)
    return render(request, 'inventory/positionview.html', {"locations": loc})


def location_detail_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    equipments = Equipment.objects.filter(location=location)
    return render(request, 'inventory/position_detail.html', {'location': location, "equipments": equipments})