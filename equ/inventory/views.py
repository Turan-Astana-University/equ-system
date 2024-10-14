from django.http import HttpResponse
from django.shortcuts import redirect
from locations.models import Location
from django.shortcuts import render, get_object_or_404
from equipments.models import Equipment
from datetime import datetime
from .models import Inventory
from django.views import View
from .mixins import SuperuserRequiredMixin

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
# Create your views here.


class LocationInventoryView(SuperuserRequiredMixin, View):
    template_name = 'inventory/locations_view.html'

    def get(self, request, *args, **kwargs):
        inventory = Inventory.objects.last()
        loc = Location.objects.all()
        location_found = loc.filter(date_last_invent__gte=inventory.date_start)
        location_non_found = loc.filter(
    date_last_invent__lte=inventory.date_start
) | loc.filter(date_last_invent__isnull=True)

        context = {
            "location_found": location_found,
            "location_non_found": location_non_found,
            "locations": loc
        }
        print(context)
        return render(request, self.template_name, context)

class EndInventLocationView(SuperuserRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        location = get_object_or_404(Location, pk=pk)
        location.date_last_invent = datetime.now()
        location.save()
        return redirect('locations')


class CreateInventView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            new_inventory = Inventory(date_start=datetime.now())
            new_inventory.save()
            return redirect("locations")
        else:
            return HttpResponse("НЕТ ДОСТУПА")


class EndInventView(SuperuserRequiredMixin, View):
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



class IndexInventView(SuperuserRequiredMixin, View):
    template_name = "inventory/inventory.html"

    def get(self, request, *args, **kwargs):
        inventory = Inventory.objects.last()
        context = {"inventory": inventory} if inventory and not inventory.date_end else {}
        return render(request, self.template_name, context)


class LocationDetailView(SuperuserRequiredMixin, View):
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









