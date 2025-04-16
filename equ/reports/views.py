import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import plotly.express as px
from equipments.models import Equipment, Printer, EquipmentType
from django.core.paginator import Paginator
from django.contrib import messages
from inventory.models import Inventory
from django.contrib.auth.mixins import LoginRequiredMixin

from locations.models import Location
from users.models import User
from .mixin import AccountingUserRequiredMixin
from django.views.generic import ListView, DetailView
from operations.models import Operation
import pandas as pd
from django.conf import settings
from equipments.models import CartridgeTypes
import requests
from inventory.mixins import AccountingRequiredMixin
from .forms import EquipmentFilterForm


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_print_request(request, zpl_code):
    """Django получает IP клиента и отправляет запрос на FastAPI"""
    if request.method == "POST":
        client_ip = get_client_ip(request)  # Получаем IP-адрес клиента

        if not zpl_code:
            return JsonResponse({"error": "Не указан zpl_data"}, status=400)

        fastapi_url = f"http://192.168.115.165:8563/print"
        print(fastapi_url)

        try:
            response = requests.post(fastapi_url, json={"zpl_data": zpl_code})
            if response:
                print("YES")
            else:
                return JsonResponse(response.json(), status=response.status_code)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Не удалось подключиться к {fastapi_url}", "details": str(e)}, status=500)

    return JsonResponse({"error": "Используйте POST-запрос"}, status=405)


class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'reports/equipment_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        equipment = self.get_object()

        context['operations'] = Operation.objects.filter(equipment=equipment)
        return context

    def post(self, request, *args, **kwargs):
        equipment = self.get_object()
        zpl_data = equipment.equipment_barcode.zpl_barcode
        try:
            response = send_print_request(request, zpl_data)
            print(response)
            if response.status_code == 500:
                messages.error(request, "Этикетка не отправлена на печать")
            else:
                messages.success(request, "Этикетка успешно отправлена на печать")

            return redirect("report_equipments")
        except Exception as e:
            return HttpResponse(f"Ошибка печати: {e}", status=500)


class EquipmentReportView(AccountingRequiredMixin, ListView):
    model = Equipment
    template_name = 'reports/report_equipments.html'
    context_object_name = 'objects'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        equipments = Equipment.objects.all()
        print("POST:", request)
        form = EquipmentFilterForm(request.GET or None)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            location = form.cleaned_data.get('location')
            responsible = form.cleaned_data.get('responsible')

            if category:
                equipments = equipments.filter(category=category)
            if location:
                equipments = equipments.filter(location=location)
            if responsible:
                equipments = equipments.filter(responsible=responsible)

        paginator = Paginator(equipments, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'form': form,
            'objects': page_obj,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = EquipmentFilterForm(request.POST or None)
        equipments = Equipment.objects.all()
        action = request.POST.get("action")

        if form.is_valid():
            category = form.cleaned_data.get('category')
            location = form.cleaned_data.get('location')
            responsible = form.cleaned_data.get('responsible')

            if category:
                equipments = equipments.filter(category=category)
            if location:
                equipments = equipments.filter(location=location)
            if responsible:
                equipments = equipments.filter(responsible=responsible)

        paginator = Paginator(equipments, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'form': form,
            "objects": page_obj
        }
        if action == "print":
            for equipment in equipments:
                zpl_data = equipment.equipment_barcode.zpl_barcode
                send_print_request(request, zpl_data)
            return render(request, self.template_name, context=context)
        return render(request, self.template_name, context=context)


class PrinterReportView(AccountingRequiredMixin, ListView):
    model = Printer
    template_name = 'reports/report_printers.html'
    context_object_name = 'objects'


class InventoryReportView(AccountingRequiredMixin, ListView):
    model = Inventory
    template_name = 'reports/report_inventorys.html'
    context_object_name = 'objects'
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        inventorys = Inventory.objects.all()
        paginator = Paginator(inventorys, self.paginate_by)

        page_number = request.GET.get('page')

        page_obj = paginator.get_page(page_number)

        context = {
            'objects': page_obj
        }
        return render(request, self.template_name, context)


class InventoryDetailView(AccountingRequiredMixin, DetailView):
    model = Inventory
    template_name = 'reports/inventory_detail.html'
    context_object_name = 'object'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        inventory = self.get_object()

        df = pd.read_excel(os.path.join(settings.MEDIA_ROOT, inventory.report.result_file.name))
        print(df.groupby('Операция').count())
        fig = px.pie(
            df,
            names='Операция',  # Параметр для названия категорий
            title="Круговая диаграмма: Отчет инвентаризации"  # Заголовок
        )
        fig.update_traces(textinfo='percent+label')


        graph_json = fig.to_json()

        context['graph_json'] = graph_json
        return context


class CartridgeReportView(AccountingRequiredMixin, ListView):
    model = CartridgeTypes
    template_name = 'reports/cartridge_types.html'
    context_object_name = 'objects'


class PackagePrint(ListView):
    model = Location
    template_name = "reports/package_print.html"

