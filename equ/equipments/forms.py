from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import admin
from .models import Cartridge, CartridgeTypes, CategoryChoices
from users.models import User
from locations.models import Location


class BulkCreateCartridgeForm(forms.Form):
    title = forms.CharField(label="Название", max_length=50)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Местоположение")
    color = forms.CharField(label="Цвет", max_length=50)
    status = forms.ChoiceField(choices=CategoryChoices.choices, label="Статус")
    responsible = forms.ModelChoiceField(queryset=User.objects.all(), label="Отв.сотрудник")
    cartridge_type = forms.ModelChoiceField(queryset=CartridgeTypes.objects.all(), label="Тип картриджа")
    count = forms.IntegerField(label="Количество", min_value=1)
