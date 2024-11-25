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


class Barcode(models.Model):
    barcode = models.ImageField(upload_to='barcodes/', blank=True, verbose_name="Штрих код")

    def generate_barcode(self):
        # Генерация штрих-кода используя python-barcode
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(f'{self.id:012}', writer=ImageWriter())  # Используем self.id, так как он будет определен после сохранения

        buffer = BytesIO()
        ean.write(buffer)

        # Сохранение штрих-кода в поле barcode
        file_name = f'{self.id}.png'
        self.barcode.save(file_name, File(buffer), save=False)


class Equipment(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Категория")
    equipment_barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True, blank=True)  # Оставляем это поле как есть
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
        if not self.equipment_barcode:  # Проверка на существование штрих-кода
            bc = Barcode.objects.create()  # Создаем новый Barcode
            bc.generate_barcode()  # Генерируем штрих-код
            bc.save()
            self.equipment_barcode = bc  # Присваиваем штрих-код
        super().save(*args, **kwargs)  # Сохраняем объект Equipment


class CartridgeTypes(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "type Картридж"
        verbose_name_plural = "type Картриджи"

    def __str__(self):
        return self.title


class CategoryChoices(models.TextChoices):
    FILLED = 'filled', ('Filled')
    NEW = 'new', ('new')
    EMPTY = 'empty', ('empty')
    DEFECTIVE = 'defective', ('defective')


class Cartridge(models.Model):
    color = models.CharField(max_length=50, verbose_name="Цвет", null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices,
        default=CategoryChoices.NEW
    )
    cartridge_type = models.ForeignKey(CartridgeTypes, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Тип картриджа")
    title = models.CharField(max_length=255, verbose_name="Название", null=True, blank=True)
    cartridge_barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True, blank=True)  # Переименовано
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Местонахождение")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ответственное лицо")
    is_true_position = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        verbose_name = "Картридж"
        verbose_name_plural = "Картриджи"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.cartridge_barcode:  # Проверка на существование штрих-кода
            bc = Barcode.objects.create()  # Создаем новый Barcode
            bc.generate_barcode()  # Генерируем штрих-код
            self.cartridge_barcode = bc  # Присваиваем штрих-код
        super().save(*args, **kwargs)  # Сохраняем объект Cartridge
