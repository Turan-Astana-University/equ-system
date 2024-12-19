from django.http import HttpResponse
from django.shortcuts import render
from equipments.models import Equipment, Printer
from django.core.paginator import Paginator
import pandas as pd
from datetime import datetime

from inventory.models import Inventory
from .models import Report
from django.core.files.base import File
from io import BytesIO
from django.contrib.contenttypes.models import ContentType
# Create your views here.


def get_report(request):
    equipments = Equipment.objects.all()
    paginator = Paginator(equipments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reports/report_equipments.html', context={"objects": page_obj})


def get_report_printer(request):
    printers = Printer.objects.all()
    return render(request, "reports/report_printers.html", context={"objects": printers})


def report_inventorys(request):
    inventorys = Inventory.objects.all()
    return render(request, 'reports/report_inventorys.html', context={'objects': inventorys})