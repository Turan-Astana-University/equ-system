from inventory.models import Inventory
from operations.models import Operation
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from reports.models import Report, CategoryChoices
from django.utils.timezone import now
from django.core.files.base import ContentFile


def create_file(request, inventory):
    # Создаем DataFrame
    df = pd.DataFrame(
        columns=[
            'Операция',
            'Оборудование',
            'Дата',
            'Прошлое местоположение',
            'Новое местоположение',
            'Прошлый ответственный сотрудник',
            'Новый ответственный сотрудник',
        ]
    )

    # Фильтруем данные
    filtered_data = Operation.objects.filter(
        date__gte=inventory.date_start,
        date__lte=inventory.date_end
    )

    # Наполняем таблицу данными
    rows = []
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
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

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