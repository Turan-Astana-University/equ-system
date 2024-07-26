from django.urls import path
from .views import location_view, location_detail_view, equ_invent_find, invent, create_invent, end_invent


urlpatterns = [
    path("", invent, name="invent"),
    # path('scan/', scan_barcode, name='scan_barcode'),
    path("locations/", location_view, name="locations"),
    path("locations/<int:pk>/", location_detail_view, name="location_detail"),
    path("invent_find", equ_invent_find, name="equ_invent_find"),
    path("create_invent/", create_invent, name="create_invent"),
    path("end_ivent", end_invent, name="end_invent")
]
