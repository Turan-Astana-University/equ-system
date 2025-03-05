from django.contrib import admin
from .models import Equipment, EquipmentType, Cartridge, CartridgeTypes, CategoryChoices, Barcode, Printer
from .forms import BulkCreateCartridgeForm
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.contrib import messages
# Register your models here.


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('equipment_barcode', 'date_last_check', 'date_last_invent')


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentType)
admin.site.register(Barcode)


@admin.register(Cartridge)
class CartridgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'status', 'cartridge_type', 'print_barcode_button']
    fields = ['title', 'color', 'status', 'cartridge_type', 'location', 'responsible', 'is_true_position']

    def print_barcode_button(self, obj):
        return format_html('<a class="button" href="{}">Напечатать штрих-код</a>',
                           f"/admin/cartridge/{obj.id}/print-barcode/")

    print_barcode_button.short_description = "Печать"

    def print_barcode_action(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj and obj.cartridge_barcode:
            response = obj.print_barcode(request)
            return response
        messages.error(request, "Штрих-код отсутствует!")
        return redirect(request.META.get("HTTP_REFERER", "admin:index"))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='bulk_create_cartridges'),
            path(
                '<int:object_id>/print-barcode/',  # Исправленный путь
                self.admin_site.admin_view(self.print_barcode_action),
                name="print_barcode"
            ),
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
                        responsible=data['responsible'],
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
admin.site.register(Printer)
# admin.site.register(Cartridge)
