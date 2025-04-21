from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import admin
from .models import Cartridge, CartridgeTypes, CategoryChoices, CategoryStatusChoices
from users.models import User
from locations.models import Location
from .models import Equipment


class BulkCreateCartridgeForm(forms.Form):
    title = forms.CharField(label="Название", max_length=50)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Местоположение")
    color = forms.CharField(label="Цвет", max_length=50)
    status = forms.ChoiceField(choices=CategoryChoices.choices, label="Статус")
    responsible = forms.ModelChoiceField(queryset=User.objects.all(), label="Отв.сотрудник")
    cartridge_type = forms.ModelChoiceField(queryset=CartridgeTypes.objects.all(), label="Тип картриджа")
    count = forms.IntegerField(label="Количество", min_value=1)


class UpdateEquipment(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['title', 'description', 'category', 'location', 'image']

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'placeholder': 'Наименование',
            'id': 'title'
        })
    )

    description = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'placeholder': 'Описание',
            'id': 'description'
        })
    )

    category = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'placeholder': 'Категория',
            'id': 'category'
        })
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label="Выберите категорию",
        widget=forms.Select(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'id': 'location'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'u-input u-input-rectangle',
            'id': 'image-upload'
        })
    )
    status = forms.ChoiceField(
        choices=CategoryStatusChoices.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'id': 'status'
        })
    )