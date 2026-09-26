from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile
from agro.models import Producer, Product
from locations.models import Address
from menus.models import RestaurantProduct
from orders.models import Order, OrderItem
from restaurants.models import Restaurant


class OrderValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.consumer = User.objects.create_user(username='consumer', password='testpass123')
        cls.other_consumer = User.objects.create_user(username='other-consumer', password='testpass123')
        cls.address = Address.objects.create(
            owner=cls.consumer,
            street='Main',
            number='123',
            city='CABA',
            province='Buenos Aires',
        )
        cls.other_address = Address.objects.create(
            owner=cls.other_consumer,
            street='Side',
            number='456',
            city='La Plata',
            province='Buenos Aires',
        )

    def test_delivery_address_must_belong_to_consumer(self):
        order = Order(
            consumer=self.consumer,
            mode=Order.Mode.RESTAURANT,
            delivery_address=self.other_address,
            total=Decimal('100.00'),
        )

        with self.assertRaises(ValidationError) as cm:
            order.full_clean()

        self.assertIn('delivery_address', cm.exception.error_dict)


class OrderItemValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.consumer = User.objects.create_user(username='consumer', password='testpass123')
        cls.producer_user = User.objects.create_user(username='producer', password='testpass123')
        cls.restaurant_owner = User.objects.create_user(username='restaurant-owner', password='testpass123')

        cls.consumer_address = Address.objects.create(
            owner=cls.consumer,
            street='Main',
            number='123',
            city='CABA',
            province='Buenos Aires',
        )
        cls.producer_address = Address.objects.create(
            owner=cls.producer_user,
            street='Farm',
            number='1',
            city='Pergamino',
            province='Buenos Aires',
        )
        cls.restaurant_address = Address.objects.create(
            owner=cls.restaurant_owner,
            street='Food',
            number='10',
            city='CABA',
            province='Buenos Aires',
        )

        producer_profile = Profile.objects.create(user=cls.producer_user, role=Profile.Role.PRODUCER)
        cls.producer = Producer.objects.create(
            profile=producer_profile,
            business_name='Farm One',
            tax_id='TAX-ORDER-001',
            address=cls.producer_address,
        )
        cls.agro_product = Product.objects.create(
            producer=cls.producer,
            name='Tomatoes',
            price=Decimal('1200.00'),
            unit=Product.Unit.KG,
        )
        cls.restaurant = Restaurant.objects.create(
            owner=cls.restaurant_owner,
            name='Bistro',
            address=cls.restaurant_address,
        )
        cls.restaurant_product = RestaurantProduct.objects.create(
            restaurant=cls.restaurant,
            name='Burger',
            price=Decimal('9500.00'),
        )
        cls.restaurant_order = Order.objects.create(
            consumer=cls.consumer,
            mode=Order.Mode.RESTAURANT,
            delivery_address=cls.consumer_address,
            total=Decimal('9500.00'),
        )
        cls.agro_order = Order.objects.create(
            consumer=cls.consumer,
            mode=Order.Mode.AGRO,
            delivery_address=cls.consumer_address,
            total=Decimal('1200.00'),
        )

    def test_order_item_requires_exactly_one_product(self):
        item_without_product = OrderItem(
            order=self.restaurant_order,
            quantity=Decimal('1.00'),
            unit_price=Decimal('9500.00'),
        )
        item_with_both_products = OrderItem(
            order=self.restaurant_order,
            restaurant_product=self.restaurant_product,
            agro_product=self.agro_product,
            quantity=Decimal('1.00'),
            unit_price=Decimal('9500.00'),
        )

        with self.assertRaisesMessage(ValidationError, 'Order item must reference exactly one product.'):
            item_without_product.full_clean()
        with self.assertRaisesMessage(ValidationError, 'Order item must reference exactly one product.'):
            item_with_both_products.full_clean()

    def test_restaurant_order_requires_restaurant_product(self):
        item = OrderItem(
            order=self.restaurant_order,
            agro_product=self.agro_product,
            quantity=Decimal('1.00'),
            unit_price=Decimal('1200.00'),
        )

        with self.assertRaises(ValidationError) as cm:
            item.full_clean()

        self.assertIn('restaurant_product', cm.exception.error_dict)

    def test_agro_order_requires_agro_product(self):
        item = OrderItem(
            order=self.agro_order,
            restaurant_product=self.restaurant_product,
            quantity=Decimal('1.00'),
            unit_price=Decimal('9500.00'),
        )

        with self.assertRaises(ValidationError) as cm:
            item.full_clean()

        self.assertIn('agro_product', cm.exception.error_dict)
