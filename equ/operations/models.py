from django.db import models
from equipments.models import Equipment
from locations.models import Location
from users.models import User
# Create your models here.


class OperationType(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"


class OperationCategoryChoices(models.TextChoices):
    RELEASE_EQUIPMENT = 'release_equipment', ("Release Equipment")
    INVENTORY = 'inventory', ("Inventory")
    MOVED_WITHOUT_NOTICE = 'moving_withour_notice', ("Moved without nothing")
    RELEASE_CARTRIDGE = 'release_cartridge', ("Release Cartridge")


class Operation(models.Model):
    operation_type = models.CharField(
        max_length=50,
        choices=OperationCategoryChoices.choices,
        default=OperationCategoryChoices.INVENTORY
    )
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    location_old = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="old_location")
    location_new = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="new_location")
    responsible_old = models.ForeignKey(User, on_delete=models.CASCADE, related_name="old_user")
    responsible_new = models.ForeignKey(User, on_delete=models.CASCADE, related_name="new_user")
