from django.test import TestCase
from django.urls import reverse

from equipments.models import Barcode, Equipment, EquipmentType
from locations.models import Location
from users.models import CategoryChoicesUser, User


class EquipmentsExportViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="accounting_user",
            password="pass",
            first_name="Test",
            last_name="User",
            staff=CategoryChoicesUser.ACCOUNTING,
        )

        self.location = Location.objects.create(title="Room 101", description="Test room")
        self.category = EquipmentType.objects.create(title="Laptop")
        self.barcode = Barcode.objects.create(zpl_barcode="")

        Equipment.objects.create(
            title="Dell",
            description="desc",
            category=self.category,
            location=self.location,
            responsible=self.user,
            equipment_barcode=self.barcode,
        )

    def test_export_csv(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("export_equipments"), {"format": "csv"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertIn("attachment;", response["Content-Disposition"])

        content = response.content.decode("utf-8-sig")
        self.assertIn("id;title;description", content)
        self.assertIn("Dell", content)

    def test_export_xlsx(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("export_equipments"), {"format": "xlsx"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response["Content-Type"].startswith(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"PK"))
