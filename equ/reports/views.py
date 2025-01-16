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


def convert_png_to_zpl(png_image_path):
    zebra.setdevice('Zebra')
    # Формируем путь к файлу изображения
    image_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', os.path.basename(png_image_path))
    print(f"Image path: {image_path}")
    print(zebra.ZPLconvert(image_path))

    # Открываем изображение с помощью PIL
    img = Image.open(image_path)

    # Открываем изображение в стандартном просмотрщике (для Windows)
    if os.name == 'nt':  # Для Windows
        os.startfile(image_path)
    elif os.name == 'posix':  # Для macOS и Linux
        os.system(f'open {image_path}')  # Для macOS
        # или для Linux:
        # os.system(f'xdg-open {image_path}')

    # Преобразуем изображение в черно-белое (1 бит)
    img = img.convert("1")

    # Преобразуем изображение в строку байтов
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()

    # Преобразуем байты в строку base64
    base64_str = base64.b64encode(byte_arr).decode("utf-8")

    # Формируем строку ZPL
    zpl_header = "^XA\n^FO50,50\n^GFA,"
    zpl_footer = "^FS\n^XZ"

    # Генерируем строку ZPL с изображением в base64
    zpl_image = f"{zpl_header}{len(byte_arr)},{len(byte_arr)},{len(byte_arr) // len(byte_arr)}," + base64_str + zpl_footer
    return zpl_image


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
        print(equipment.equipment_barcode)
        print((equipment.equipment_barcode.barcode.url))
        zpl_data = convert_png_to_zpl(equipment.equipment_barcode.barcode.url)
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
        # Получаем все объекты Equipment
        equipments = Equipment.objects.all()

        # Создаем объект Paginator для пагинации
        paginator = Paginator(equipments, self.paginate_by)

        # Получаем номер страницы из GET-параметров
        page_number = request.GET.get('page')

        # Получаем текущую страницу с данными
        page_obj = paginator.get_page(page_number)

        # Передаем контекст в шаблон
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
