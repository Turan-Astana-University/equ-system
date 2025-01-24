from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from equipments.models import Equipment, Printer
from django.core.paginator import Paginator

from inventory.models import Inventory
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixin import AccountingUserRequiredMixin
from django.views.generic import ListView, DetailView
import win32print
from PIL import Image
import base64
from io import BytesIO
from django.conf import settings
import os
import io
from PIL import Image
import zebra


def print_test_label(zpl_data):
    printer_name = "ZDesigner ZD220-203dpi ZPL"  # Укажите имя вашего принтера

    try:
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        if printer_name not in printers:
            print(f"Принтер '{printer_name}' не найден. Доступные принтеры: {printers}")
            return

        printer = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(printer, 1, ("Test Print", None, "RAW"))
            win32print.StartPagePrinter(printer)
            bytes_written = win32print.WritePrinter(printer, zpl_data.encode('utf-8'))
            win32print.EndPagePrinter(printer)
            win32print.EndDocPrinter(printer)
            print(f"Этикетка успешно отправлена на печать! Байтов отправлено: {bytes_written}")
        finally:
            win32print.ClosePrinter(printer)
    except Exception as e:
        print(f"Ошибка печати: {e}")


class EquipmentDetailView(LoginRequiredMixin, AccountingUserRequiredMixin, DetailView):
    model = Equipment
    template_name = 'reports/equipment_detail.html'
    context_object_name = 'object'

    def post(self, request, *args, **kwargs):
        equipment = self.get_object()
        zpl_data = equipment.equipment_barcode.zpl_barcode
        try:
            print_test_label(zpl_data)
            return HttpResponse("Этикетка успешно отправлена на печать!")
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
