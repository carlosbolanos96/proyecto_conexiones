from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile
from delivery.models import Courier, Delivery
from locations.models import Address
from orders.models import Order


class CourierValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.consumer_user = User.objects.create_user(username='consumer', password='testpass123')
        cls.courier_user = User.objects.create_user(username='courier', password='testpass123')
        cls.consumer_profile = Profile.objects.create(user=cls.consumer_user, role=Profile.Role.CONSUMER)
        cls.courier_profile = Profile.objects.create(user=cls.courier_user, role=Profile.Role.COURIER)

    def test_profile_must_have_courier_role(self):
        courier = Courier(profile=self.consumer_profile, vehicle_type=Courier.Vehicle.BIKE)

        with self.assertRaises(ValidationError) as cm:
            courier.full_clean()

        self.assertIn('profile', cm.exception.error_dict)

    def test_profile_with_courier_role_passes_validation(self):
        courier = Courier(profile=self.courier_profile, vehicle_type=Courier.Vehicle.BIKE)

        courier.full_clean()


class DeliveryValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.consumer = User.objects.create_user(username='delivery-consumer', password='testpass123')
        cls.address = Address.objects.create(
            owner=cls.consumer,
            street='Main',
            number='123',
            city='CABA',
            province='Buenos Aires',
        )
        cls.agro_order = Order.objects.create(
            consumer=cls.consumer,
            mode=Order.Mode.AGRO,
            delivery_address=cls.address,
            total=Decimal('100.00'),
        )

    def test_delivery_is_only_allowed_for_restaurant_orders(self):
        delivery = Delivery(order=self.agro_order)

        with self.assertRaises(ValidationError) as cm:
            delivery.full_clean()

        self.assertIn('order', cm.exception.error_dict)
