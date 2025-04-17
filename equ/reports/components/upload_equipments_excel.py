import pandas as pd
from django.shortcuts import render
from equipments.models import Equipment, EquipmentType
from users.models import User
from locations.models import Location


def upload_excel_view(request):
    excel_file = request.FILES['file']
    df = pd.read_csv(excel_file)
    df = df.dropna()
    for index, row in df.iterrows():
        title_excel = row['Название']
        responsible_excel = row["Имя пользователя"]
        name_excel = row['Отвественное лицо']
        category_excel = row['Категория']
        location_excel = row['Местоположение']

        if not responsible_excel or not category_excel or not location_excel or not name_excel or not title_excel:
            break
        print(category_excel)
        if category_excel == "nan":
            print(title_excel)
            break
        user = User.objects.filter(username=responsible_excel)
        if not user:
            user = User(username=responsible_excel, first_name=name_excel.split()[0], last_name=name_excel.split()[1], email="info@tau-edu.kz")
            user.save()
        else:
            user = user.first()

        locations = Location.objects.filter(title=location_excel)
        if not locations:
            location = Location(title=location_excel, description="msexcel", responsible=user)
            location.save()
        else:
            location = locations.first()

        categories = EquipmentType.objects.filter(title=category_excel)
        if not categories:
            category = EquipmentType(title=category_excel)
            category.save()
        else:
            category = categories.first()

        Equipment(title=title_excel,category=category, description="MsExcel", location=location, responsible=user).save()

