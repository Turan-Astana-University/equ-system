from django.http import HttpResponse
from django.shortcuts import render
from equipments.models import Equipment, Printer
from django.core.paginator import Paginator
import pandas as pd
from datetime import datetime
from .models import Report
from django.core.files.base import File
from io import BytesIO
from django.contrib.contenttypes.models import ContentType
# Create your views here.


def get_report(request):
    # df = pd.DataFrame(
    #     {"Название", "Местоположение", "Отв.лицо", "Категория"}
    # )
    equipments = Equipment.objects.all()
    paginator = Paginator(equipments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = []
    # for equipment in equipments:
    #     data.append({
    #         "Название": equipment.title,
    #         "Местоположение": equipment.location,
    #         "Отв.лицо": equipment.responsible,
    #         "Категория": equipment.category
    #     })
    #
    # df = pd.DataFrame(data)
    # output_buffer = BytesIO()
    # df.to_excel(output_buffer, index=False, engine='openpyxl')
    # output_buffer.seek(0)
    # output_file_name = f"reports_{datetime.now().date()}.xlsx"
    # report = Report.objects.create(
    #     title=f"Отчёт за {datetime.now().date()}",
    #     date=datetime.now()
    # )
    # report.result_file.save(output_file_name, File(output_buffer))
    # output_buffer.close()
    return render(request, 'reports/report_equipments.html', context={"objects": page_obj})


def get_report_printer(request):
    printers = Printer.objects.all()
    return render(request, "reports/report_printers.html", context={"objects": printers})


#
# def generate_word(request):
#     inventory = Inventory.objects.last()
#     df = pd.DataFrame(
#         {
#             'Операция',
#             'Оборудование',
#             'Дата',
#             'Прошлое местоположение',
#             'Новое местоположение',
#             'Прошлый ответственный сотрудник',
#             'Новый ответственный сотрудник'
#         }
#     )
#     filtered_data = Operation.objects.filter(
#         date__gte=inventory.date_start,
#         date__lte=inventory.date_end
#     )
#     rows = []
#     for row in filtered_data:
#         rows.append({
#             'Операция': row.operation_type,
#             'Оборудование': row.equipment.title,
#             'Дата': row.date.replace(tzinfo=None),
#             'Прошлое местоположение': row.location_old.title,
#             'Новое местоположение': row.location_new.title,
#             'Прошлый ответственный сотрудник': f"{row.responsible_old.first_name} {row.responsible_old.last_name} - {row.responsible_old}",
#             'Новый ответственный сотрудник': rf"{row.responsible_new.first_name} {row.responsible_new.last_name} - {row.responsible_new}",
#
#         })
#     df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
#     output = BytesIO()
#     df.to_excel(output, index=False, engine='openpyxl')
#     output.seek(0)
#
#     response = HttpResponse(
#         output,
#         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
#     response['Content-Disposition'] = 'attachment; filename="inventory_operations.xlsx"'
#
#     return response
