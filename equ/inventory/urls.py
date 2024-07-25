from django.urls import path
from .views import location_view, location_detail_view, equ_invent_find
urlpatterns = [
    # path('scan/', scan_barcode, name='scan_barcode'),
    path("locations/", location_view, name="location"),
    path("locations/<int:pk>/", location_detail_view, name="location_detail"),
    path("invent_find", equ_invent_find, name="equ_invent_find"),
]
