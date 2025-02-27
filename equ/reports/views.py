import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import plotly.express as px
from equipments.models import Equipment, Printer
from django.core.paginator import Paginator
from django.contrib import messages
from inventory.models import Inventory
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixin import AccountingUserRequiredMixin
from django.views.generic import ListView, DetailView
from operations.models import Operation
import pandas as pd
from django.conf import settings
from equipments.models import CartridgeTypes
import requests


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Берем первый IP в цепочке
    else:
        ip = request.META.get('REMOTE_ADDR')  # Обычный IP, если прокси нет
    return ip


def send_print_request(request, zpl_code):
    """Django получает IP клиента и отправляет запрос на FastAPI"""
    if request.method == "POST":
        client_ip = get_client_ip(request)  # Получаем IP-адрес клиента

        if not zpl_code:
            return JsonResponse({"error": "Не указан zpl_data"}, status=400)

        # Формируем URL FastAPI сервера на клиентском IP
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


class EquipmentDetailView(LoginRequiredMixin, DetailView):
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

            # Перенаправляем на предыдущую страницу
            return redirect("report_equipments")
        except Exception as e:
            return HttpResponse(f"Ошибка печати: {e}", status=500)


class EquipmentReportView(LoginRequiredMixin, AccountingUserRequiredMixin, ListView):
    model = Equipment
    template_name = 'reports/report_equipments.html'
    context_object_name = 'objects'  # Соответствует вашему шаблону
    paginate_by = 10  # Количество объектов на странице

    def get(self, request, *args, **kwargs):
        equipments = Equipment.objects.all()
        paginator = Paginator(equipments, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'objects': page_obj
        }
        client_ip = get_client_ip(request)
        return render(request, self.template_name, context)


# Класс для списка принтеров
class PrinterReportView(LoginRequiredMixin, AccountingUserRequiredMixin, ListView):
    model = Printer
    template_name = 'reports/report_printers.html'
    context_object_name = 'objects'


# Класс для списка инвентарей
class InventoryReportView(LoginRequiredMixin, AccountingUserRequiredMixin, ListView):
    model = Inventory
    template_name = 'reports/report_inventorys.html'
    context_object_name = 'objects'
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        inventorys = Inventory.objects.all()
        paginator = Paginator(inventorys, self.paginate_by)

        # Получаем номер страницы из GET-параметров
        page_number = request.GET.get('page')

        # Получаем текущую страницу с данными
        page_obj = paginator.get_page(page_number)

        # Передаем контекст в шаблон
        context = {
            'objects': page_obj
        }
        return render(request, self.template_name, context)


class InventoryDetailView(LoginRequiredMixin, AccountingUserRequiredMixin, DetailView):
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


        graph_json = fig.to_json()  # Конвертируем график в JSON

        context['graph_json'] = graph_json
        return context


class CartridgeReportView(LoginRequiredMixin, AccountingUserRequiredMixin, ListView):
    model = CartridgeTypes
    template_name = 'reports/cartridge_types.html'
    context_object_name = 'objects'
