from django.contrib import admin
from .models import Equipment, EquipmentType, Cartridge, CartridgeTypes, CategoryChoices, Barcode
from .forms import BulkCreateCartridgeForm
from django.urls import path
from django.shortcuts import render, redirect
# Register your models here.


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('equipment_barcode', 'date_last_check', 'date_last_invent')


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentType)
admin.site.register(Barcode)


@admin.register(Cartridge)
class CartridgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'status', 'cartridge_type']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='bulk_create_cartridges'),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == 'POST':
            form = BulkCreateCartridgeForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                cartridges = []

                for _ in range(data['count']):
                    # Создаем новый объект Barcode
                    barcode = Barcode()
                    barcode.generate_barcode()  # Генерируем штрих-код
                    barcode.save()  # Сохраняем штрих-код

                    # Создаем новый картридж с добавленным штрих-кодом
                    cartridge = Cartridge(
                        title=data['title'],
                        color=data['color'],
                        status=data['status'],
                        cartridge_type=data['cartridge_type'],
                        cartridge_barcode=barcode  # Добавляем сгенерированный штрих-код
                    )
                    cartridges.append(cartridge)

                # Массово сохраняем картриджи
                Cartridge.objects.bulk_create(cartridges)

                self.message_user(request, f"{len(cartridges)} новых картриджей успешно созданы.")
                return redirect("../")  # Возвращаемся в админку
        else:
            form = BulkCreateCartridgeForm()

        context = {
            'form': form,
            'title': "Массовое создание картриджей"
        }
        return render(request, 'equipments/bulk_create_cartridges.html', context)

admin.site.register(CartridgeTypes)
# admin.site.register(Cartridge)
