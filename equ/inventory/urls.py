from django.urls import path
from .views import LocationInventoryView, LocationDetailView, IndexInventView, CreateInventView, EndInventView, EndInventLocationView


urlpatterns = [
    path("", IndexInventView.as_view(), name="invent"),
    path("locations/", LocationInventoryView.as_view(), name="locations"),
    path("locations/<int:pk>/", LocationDetailView.as_view(), name="location_detail"),
    path("create_invent/", CreateInventView.as_view(), name="create_invent"),
    path("end_invent/", EndInventView.as_view(), name="end_invent"),
    path("end_invent_location/<int:pk>", EndInventLocationView.as_view(), name="end_invent_location")
]
