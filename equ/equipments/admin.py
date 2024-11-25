from django.contrib import admin
from .models import Equipment, EquipmentType, Cartridge, CartridgeTypes, CategoryChoices
# Register your models here.


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('barcode', 'date_last_check', 'date_last_invent')


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentType)
#
#
# class CartridgeAdmin(admin.ModelAdmin):
#     list_display = ['title']
#     readonly_fields = ('barcode', 'date_last_check', 'date_last_invent')
#


@admin.register(Cartridge)
class CartridgeAdmin(admin.ModelAdmin):
    list_display = ['color', 'status', 'cartridge_type']

    # Кастомное действие
    actions = ['create_multiple_cartridges']

    def create_multiple_cartridges(self, request, queryset):
        # Создать 10 новых картриджей с одинаковым параметром
        cartridge_type = CartridgeTypes.objects.first()  # Замените на нужный тип
        cartridges = [
            Cartridge(
                color="Black",
                status=CategoryChoices.NEW,
                cartridge_type=cartridge_type
            )
            for _ in range(10)  # Укажите количество записей
        ]
        Cartridge.objects.bulk_create(cartridges)
        self.message_user(request, f"{len(cartridges)} новых картриджей успешно созданы.")

    create_multiple_cartridges.short_description = "Создать 10 новых картриджей"


admin.site.unregister(Cartridge)
admin.site.register(Cartridge, CartridgeAdmin)
admin.site.register(CartridgeTypes)
