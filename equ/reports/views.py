from django.http import HttpResponse
from django.shortcuts import render
from equipments.models import Equipment, Printer
import pandas as pd
from datetime import datetime
from .models import Report
from django.core.files.base import File
from io import BytesIO
# Create your views here.


def get_report(request):
    df = pd.DataFrame(
        {"Название", "Местоположение", "Отв.лицо", "Категория"}
    )
    equipments = Equipment.objects.all()
    data = []
    for equipment in equipments:
        data.append({
            "Название": equipment.title,
            "Местоположение": equipment.location,
            "Отв.лицо": equipment.responsible,
            "Категория": equipment.category
        })

    df = pd.DataFrame(data)
    output_buffer = BytesIO()
    df.to_excel(output_buffer, index=False, engine='openpyxl')
    output_buffer.seek(0)
    output_file_name = f"reports_{datetime.now().date()}.xlsx"
    report = Report.objects.create(
        title=f"Отчёт за {datetime.now().date()}",
        date=datetime.now()
    )
    report.result_file.save(output_file_name, File(output_buffer))
    output_buffer.close()
    return render(request, 'reports/index.html', context={"objects": equipments})


def get_report_printer(request):
    printers = Printer.objects.all()
    return render(request, "reports/index.html", context={"objects": printers})