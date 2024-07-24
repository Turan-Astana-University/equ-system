from django.contrib import admin
from .models import Equipment, EquipmentType
# Register your models here.


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('barcode', 'date_last_check', 'date_last_invent')


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentType)