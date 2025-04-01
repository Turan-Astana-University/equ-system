
import plotly.express as px
from django.shortcuts import render
import pandas as pd
from equipments.models import Equipment, EquipmentType
from inventory.mixins import SuperuserRequiredMixin, AccountingRequiredMixin
from django.views import View
from django.db.models import Count
from operations.models import Operation, OperationCategoryChoices


class DashboardView(AccountingRequiredMixin, View):
    template_name = 'dashboards/dashboard.html'

    def get(self, request, *args, **kwargs):
        data = Equipment.objects.values('title', 'location', 'category__title')
        df = pd.DataFrame(data)

        fig = px.pie(
            df,
            names='category__title',
            title="Круговая диаграмма: Категории и Количество"
        )
        fig.update_traces(textinfo='percent+label')

        graph_json = fig.to_json()

        return render(request, self.template_name, {'graph_json': graph_json})


def cartridge_usage_by_department(request):
    cartridge_usage = (
        Operation.objects.filter(operation_type=OperationCategoryChoices.RELEASE_CARTRIDGE)
        .values("responsible_new__department__title")
        .annotate(usage_count=Count("cartridge"))
        .order_by("-usage_count")
    )

    return render(request, "dashboards/cartridge_usage.html", {"cartridge_usage": cartridge_usage})