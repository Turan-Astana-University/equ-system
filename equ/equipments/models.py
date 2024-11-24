from django.db import models
from users.models import User
from django.core.files import File
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from locations.models import Location
# Create your models here.


class EquipmentType(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"


class Equipment(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    # image = models.ImageField(null=True, blank=True)
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Категория")
    barcode = models.ImageField(upload_to='barcodes/', blank=True, verbose_name="Штрих код")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Местонахождение")
    date_last_invent = models.DateTimeField(blank=True, null=True, verbose_name="Дата последней инвентаризации")
    date_last_check = models.DateTimeField(blank=True, null=True, verbose_name="Дата последней проверки")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ответственное лицо")
    image = models.ImageField(upload_to='equipment_images/', null=True, blank=True, verbose_name="Изображение")
    is_true_position = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.barcode:
            self.generate_barcode()
            super(Equipment, self).save(*args, **kwargs)

    def generate_barcode(self):
        # Генерация штрих-кода используя python-barcode
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(f'{self.pk:012}', writer=ImageWriter())

        buffer = BytesIO()
        ean.write(buffer)

        # Сохранение штрих-кода в поле barcode
        file_name = f'{self.pk}.png'
        self.barcode.save(file_name, File(buffer), save=False)


class CartridgeTypes(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "type Картридж"
        verbose_name_plural = "type Картриджи"


class CategoryChoices(models.TextChoices):
    FILLED = 'filled', ('Filled')
    NEW = 'new', ('new')
    EMPTY = 'empty', ('empty')
    DEFECTIVE = 'defective', ('defective')


class Cartridge(Equipment):
    color = models.CharField(max_length=50, verbose_name="Цвет", null=True, blank=True,)
    status = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices,
        default=CategoryChoices.NEW
    )
    cartridge_type = models.ForeignKey(CartridgeTypes, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Тип катриджа")

    class Meta:
        verbose_name = "Картридж"
        verbose_name_plural = "Картриджи"