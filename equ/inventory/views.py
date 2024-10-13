from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
from datetime import datetime
from operations.models import Operation, OperationType
from .models import Inventory
from django.views import View
# Create your views here.


class LocationInventoryView(View):
    template_name = 'inventory/locations_view.html'

    def get(self, request, *args, **kwargs):
        inventory = Inventory.objects.last()
        loc = Location.objects.all()
        location_found = loc.filter(date_last_invent__gte=inventory.date_start)
        location_non_found = loc.filter(date_last_invent__lte=inventory.date_start)

        context = {
            "location_found": location_found,
            "location_non_found": location_non_found,
            "locations": loc
        }
        return render(request, self.template_name, context)

class EndInventLocationView(View):
    def get(self, request, pk, *args, **kwargs):
        location = get_object_or_404(Location, pk=pk)
        location.date_last_invent = datetime.now()
        location.save()
        return redirect('locations')


class CreateInventView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            new_inventory = Inventory(date_start=datetime.now())
            new_inventory.save()
            return redirect("locations")
        else:
            return HttpResponse("НЕТ ДОСТУПА")


class EndInventView(View):
    def get(self, request, *args, **kwargs):
        inventory = Inventory.objects.last()
        if inventory.date_end:
            return HttpResponse(status=400)

        inventory.date_end = datetime.now()
        inventory.save()
        for equipment in Equipment.objects.all():
            equipment.is_true_position = True
            equipment.save()
        return redirect("home")


class IndexInventView(View):
    template_name = "inventory/inventory.html"

    def get(self, request, *args, **kwargs):
        inventory = Inventory.objects.last()
        context = {"inventory": inventory} if inventory and not inventory.date_end else {}
        return render(request, self.template_name, context)


class LocationDetailView(View):
    template_name = 'inventory/location_detail.html'

    def get(self, request, pk, *args, **kwargs):
        location = get_object_or_404(Location, pk=pk)
        equipments = Equipment.objects.filter(location=location)
        equipments_true = equipments.filter(is_true_position=True)
        equipments_false = equipments.filter(is_true_position=False)
        inventory = Inventory.objects.last()

        equipment_non_date_last_invent = equipments.filter(date_last_invent__isnull=True)
        equipments_found = equipments_true.filter(date_last_invent__gte=inventory.date_start)
        equipments_non_found = equipments_true.filter(date_last_invent__lte=inventory.date_start).union(
            equipment_non_date_last_invent)

        context = {
            'location': location,
            'equipments_non_found': equipments_non_found,
            'equipments_found': equipments_found,
            'equipments_false': equipments_false
        }

        return render(request, self.template_name, context)


# Не нужное
#
# def equ_invent_find(request):
#     if request.method == "POST":
#         equipment_id = request.POST.get('equipment_id')
#         equ = Equipment.objects.get(id=equipment_id)
#         location = Location.objects.get(id=request.POST.get('location_id'))
#
#         if equ.location != location:
#             Operation(date=datetime.now(), operation_type=OperationType.objects.get(pk=1), user=request.user, equipment=equ, location_old=equ.location, location_new=location, responsible_old=equ.responsible,
#                       responsible_new=location.responsible).save()
#             equ.location = location
#             equ.responsible = location.responsible
#             equ.is_true_position = False
#             equ.save()
#             return JsonResponse({
#                 'message': 'Equipment found',
#                 'equipment': equ.title,
#                 'location_correct': False
#             })
#
#         equ.date_last_invent = datetime.now()
#         equ.save()
#         return JsonResponse({
#             'message': 'Equipment found',
#             'location_correct': True
#         })
#     return HttpResponse(status=400)









