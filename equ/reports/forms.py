from django import forms
from equipments.models import EquipmentType
from locations.models import Location
from users.models import User


class EquipmentFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=EquipmentType.objects.all(),
        required=False,  # Если поле необязательное
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        empty_label="Все местоположения",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    responsible = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Все сотрудники",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )


class EquipmentsUploadForm(forms.Form):
    file = forms.FileField(
        required=True,  # Обязательно или нет
        label='Загрузите csv файл',
        help_text='Поддерживаются только .csv',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.csv'  # Ограничение на типы файлов в диалоге выбора
        })
    )