from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
from .models import Equipment


def scan_barcode(request):
    if request.method == 'POST':
        image = request.FILES['barcode_image']
        img = Image.open(image)
        decoded_objects = decode(img)

        if decoded_objects:
            barcode_data = decoded_objects[0].data.decode('utf-8')[:-1]
            print("Decoded barcode data:", barcode_data[:-1])  # Отладочная информация

            try:
                product_id = int(barcode_data)
                equipment = get_object_or_404(Equipment, pk=product_id)
                return render(request, 'equipments/scan_result.html', {
                    'equipment': equipment
                })
            except (ValueError, Equipment.DoesNotExist):
                return JsonResponse({'error': 'Invalid barcode or product not found'}, status=400)
        else:
            return JsonResponse({'error': 'No barcode found'}, status=400)

    return render(request, 'equipments/index.html')