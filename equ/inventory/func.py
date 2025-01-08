from datetime import datetime
from django.db.models import Q
from equipments.models import Equipment
from inventory.models import Inventory
from operations.models import Operation, OperationCategoryChoices
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from reports.models import Report, CategoryChoices
from django.utils.timezone import now
from django.core.files.base import ContentFile


def create_file(request, inventory):
    # Создаем DataFrame
    rows = []

    # Фильтруем данные операций
    filtered_data = Operation.objects.filter(
        date__gte=inventory.date_start,
        operation_type__in=['INVENTORY', 'MOVED_WITHOUT_NOTICE']
    )

    # Фильтруем данные оборудования, которые не найдены
    equipments_non_found = Equipment.objects.filter(
        Q(date_last_invent__lte=inventory.date_start) | Q(date_last_invent__isnull=True)
    )

    # Добавляем строки для операций
    for row in filtered_data:
        rows.append({
            'Операция': row.operation_type,
            'Оборудование': row.equipment.title,
            'Дата': row.date.replace(tzinfo=None),
            'Прошлое местоположение': row.location_old.title,
            'Новое местоположение': row.location_new.title,
            'Прошлый ответственный сотрудник': f"{row.responsible_old.first_name} {row.responsible_old.last_name} - {row.responsible_old}",
            'Новый ответственный сотрудник': f"{row.responsible_new.first_name} {row.responsible_new.last_name} - {row.responsible_new}",
        })

    # Добавляем строки для оборудования, которое не найдено
    for equipment in equipments_non_found:
        rows.append({
            'Операция': "Не найдено",
            'Оборудование': equipment.title,
            'Дата': "",
            'Прошлое местоположение': equipment.location,
            'Новое местоположение': equipment.location,
            'Прошлый ответственный сотрудник': f"{equipment.responsible.first_name} {equipment.responsible.last_name} - {equipment.responsible}",
            'Новый ответственный сотрудник': f"{equipment.responsible.first_name} {equipment.responsible.last_name} - {equipment.responsible}",
        })

    # Создаем DataFrame один раз
    df = pd.DataFrame(rows)

    # Генерация Excel-файла
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    # Сохраняем файл в модели Report
    date = now()
    report = Report(title=f"Отчёт за {date.date()}", date=date, category_report=CategoryChoices.INVENTORY)
    report.result_file.save(f"inventory_report_{now().strftime('%Y%m%d_%H%M%S')}.xlsx", ContentFile(output.read()))
    output.close()

    return report