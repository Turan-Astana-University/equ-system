from django.db import models
from users.models import User
from django.core.files import File
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from locations.models import Location
# Create your models here.


class EquipmentType(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"


class Barcode(models.Model):
    barcode = models.ImageField(upload_to='barcodes/', blank=True, verbose_name="Штрих код")
    zpl_barcode = models.TextField(null=True, blank=True)

    def generate_barcode(self, title=None):
        # Step 1: Определяем базовый штрих-код
        barcode_data = f'{self.id:012}'  # Унифицированное представление

        # Step 2: Генерация изображения
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(barcode_data, writer=ImageWriter())

        buffer = BytesIO()
        ean.write(buffer)
        buffer.seek(0)
        barcode_image = Image.open(buffer)

        barcode_height = barcode_image.height
        padding = 20
        new_height = barcode_height + padding + 100
        new_image = Image.new("RGB", (barcode_image.width, new_height), "white")
        new_image.paste(barcode_image, (0, 0))

        if title:
            draw = ImageDraw.Draw(new_image)
            try:
                font = ImageFont.truetype("arial.ttf", size=24)
            except IOError:
                font = ImageFont.load_default()

            max_length = 20
            lines = [title[i:i + max_length] for i in range(0, len(title), max_length)]
            line_height = draw.textbbox((0, 0), "A", font=font)[3]
            y_start = barcode_height + padding

            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (new_image.width - text_width) // 2
                y = y_start + i * line_height
                draw.text((x, y), line, font=font, fill="black")

        final_buffer = BytesIO()
        new_image.save(final_buffer, format='PNG')
        final_buffer.seek(0)

        file_name = f'{self.id}.png'
        self.barcode.save(file_name, File(final_buffer), save=False)

        # Step 3: Генерация ZPL-кода
        label_width = 55 * 10  # 55 мм = 550 точек
        label_height = 38 * 10  # 38 мм = 380 точек

        text_width = len(title) * 10 if title else 0  # Примерная ширина текста
        text_x = (label_width - text_width) // 2 if title else 0
        text_y = 100  # Смещение текста от верхнего края

        barcode_width = 200  # Ширина штрих-кода
        barcode_x = (label_width - barcode_width) // 2
        barcode_y = 150  # Смещение штрих-кода от верхнего края

        zpl_code = f"""
        ^XA^CI28
        ^PW530
        ^LL400

        ^FO100,50^A0,30,30^FDTuran-Astana University^FS  ; <-- Добавлен текст над штрих-кодом

        ^FO100,100^BY3
        ^BEN,100,Y,N
        ^FD{barcode_data}^FS

        ^FO100,220^A0,30,30
        ^FO{(530 - len(title) * 24) // 2},250^A0,40,40
        ^FD{title}^FS
        ^XZ"""

        self.zpl_barcode = zpl_code
        self.save()


class CategoryStatusChoices(models.TextChoices):
    BROKEN = 'неисправен', ('Неисправен')
    NEW = 'Новое', ('новое')
    RENOVATED = 'отремонтировано', ('Отремонтировано')


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
    status = models.CharField(max_length=144, choices=CategoryStatusChoices.choices, default=CategoryStatusChoices.NEW)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.equipment_barcode:  # Проверка на существование штрих-кода
            bc = Barcode.objects.create()  # Создаем новый Barcode
            bc.generate_barcode(self.title)  # Генерируем штрих-код
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

    def get_count_cartridge(self):
        cartridge = Cartridge.objects.filter(cartridge_type=self)
        return len(cartridge)


class Printer(Equipment):
    cartridge_types = models.ManyToManyField(CartridgeTypes)

    def __str__(self):
        return self.title

    def get_count_related_cartridges(self):
        cartridge_types = self.cartridge_types.all()

        # Находим все Cartridge, связанные с этими cartridge_types
        related_cartridges = Cartridge.objects.filter(cartridge_type__in=cartridge_types)
        print(related_cartridges)
        return len(related_cartridges)

    def get_cartridge_types(self):
        cartridge_types = self.cartridge_types.all()
        result = ", ".join(str(cartridge_type) for cartridge_type in cartridge_types)
        return result


class CategoryChoices(models.TextChoices):
    FILLED = 'filled', ('Filled')
    NEW = 'new', ('New')
    EMPTY = 'empty', ('Empty')
    DEFECTIVE = 'defective', ('Defective')
    RELEASE = 'release', ('Release')


class Cartridge(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название", null=True, blank=True)

    color = models.CharField(max_length=50, verbose_name="Цвет", null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices,
        default=CategoryChoices.NEW
    )
    cartridge_type = models.ForeignKey(CartridgeTypes, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Тип картриджа")
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
            bc.generate_barcode(self.title)  # Генерируем штрих-код
            self.cartridge_barcode = bc  # Присваиваем штрих-код
        super().save(*args, **kwargs)  # Сохраняем объект Cartridge
