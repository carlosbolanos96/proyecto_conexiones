from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile
from agro.models import Producer, Product
from inventory.models import InventoryItem
from locations.models import Address
from warehouses.models import Warehouse


class InventoryItemValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.producer_user = User.objects.create_user(username='producer-one', password='testpass123')
        cls.other_producer_user = User.objects.create_user(username='producer-two', password='testpass123')
        cls.producer_address = Address.objects.create(
            owner=cls.producer_user,
            street='Farm',
            number='1',
            city='Pergamino',
            province='Buenos Aires',
        )
        cls.other_producer_address = Address.objects.create(
            owner=cls.other_producer_user,
            street='Field',
            number='2',
            city='Rafaela',
            province='Santa Fe',
        )
        cls.producer_profile = Profile.objects.create(user=cls.producer_user, role=Profile.Role.PRODUCER)
        cls.other_producer_profile = Profile.objects.create(user=cls.other_producer_user, role=Profile.Role.PRODUCER)
        cls.producer = Producer.objects.create(
            profile=cls.producer_profile,
            business_name='Farm One',
            tax_id='TAX-INV-001',
            address=cls.producer_address,
        )
        cls.other_producer = Producer.objects.create(
            profile=cls.other_producer_profile,
            business_name='Farm Two',
            tax_id='TAX-INV-002',
            address=cls.other_producer_address,
        )
        cls.warehouse = Warehouse.objects.create(
            producer=cls.producer,
            name='Main Warehouse',
            address=cls.producer_address,
        )
        cls.other_product = Product.objects.create(
            producer=cls.other_producer,
            name='Potatoes',
            price=Decimal('700.00'),
            unit=Product.Unit.KG,
        )

    def test_product_must_belong_to_same_producer_as_warehouse(self):
        item = InventoryItem(
            warehouse=self.warehouse,
            product=self.other_product,
            quantity=Decimal('10.00'),
        )

        with self.assertRaises(ValidationError) as cm:
            item.full_clean()

        self.assertIn('product', cm.exception.error_dict)
