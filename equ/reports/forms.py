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