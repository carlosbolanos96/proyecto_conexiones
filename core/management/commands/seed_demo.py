from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from agro.models import Producer, Product
from delivery.models import Courier, Delivery
from inventory.models import InventoryItem
from locations.models import Address
from menus.models import RestaurantProduct
from notifications.models import Notification
from orders.models import Order, OrderItem
from payments.models import Payment
from restaurants.models import Restaurant
from warehouses.models import Warehouse


DEMO_PREFIX = 'demo_'
DEMO_ADMIN_USERNAME = 'admin'
DEMO_ADMIN_PASSWORD = 'admin12345'


class Command(BaseCommand):
    help = 'Create consistent demo data for the admin.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help=(
                f'Also create/reset the "{DEMO_ADMIN_USERNAME}" superuser so a new '
                'developer can log into /admin without running createsuperuser.'
            ),
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self._delete_demo_data()
            counts = self._create_demo_data()

        if options['create_admin']:
            self._create_demo_admin()

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        for model_name, count in counts.items():
            self.stdout.write(f'{model_name}: {count}')

    def _create_demo_admin(self):
        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username=DEMO_ADMIN_USERNAME,
            defaults={'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'Demo'},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(DEMO_ADMIN_PASSWORD)
        admin.save()

        action = 'Created' if created else 'Reset'
        self.stdout.write(
            self.style.WARNING(
                f'{action} superuser "{DEMO_ADMIN_USERNAME}" with password '
                f'"{DEMO_ADMIN_PASSWORD}". Demo credentials - never use outside local dev.'
            )
        )

    def _delete_demo_data(self):
        User = get_user_model()
        demo_users = User.objects.filter(username__startswith=DEMO_PREFIX)

        Delivery.objects.filter(order__consumer__in=demo_users).delete()
        Payment.objects.filter(order__consumer__in=demo_users).delete()
        OrderItem.objects.filter(order__consumer__in=demo_users).delete()
        Order.objects.filter(consumer__in=demo_users).delete()

        InventoryItem.objects.filter(warehouse__producer__profile__user__in=demo_users).delete()
        Warehouse.objects.filter(producer__profile__user__in=demo_users).delete()
        Product.objects.filter(producer__profile__user__in=demo_users).delete()
        Producer.objects.filter(profile__user__in=demo_users).delete()

        RestaurantProduct.objects.filter(restaurant__owner__in=demo_users).delete()
        Restaurant.objects.filter(owner__in=demo_users).delete()

        Courier.objects.filter(profile__user__in=demo_users).delete()
        Notification.objects.filter(user__in=demo_users).delete()
        Profile.objects.filter(user__in=demo_users).delete()
        Address.objects.filter(owner__in=demo_users).delete()
        demo_users.delete()

    def _create_demo_data(self):
        User = get_user_model()

        users = {}
        for username, first_name, last_name in [
            ('demo_consumer_1', 'Ana', 'Gomez'),
            ('demo_consumer_2', 'Bruno', 'Silva'),
            ('demo_consumer_3', 'Carla', 'Rojas'),
            ('demo_producer_1', 'Diego', 'Huerta'),
            ('demo_producer_2', 'Elena', 'Campo'),
            ('demo_producer_3', 'Federico', 'Verde'),
            ('demo_courier_1', 'Gaston', 'Rueda'),
            ('demo_courier_2', 'Helena', 'Moto'),
            ('demo_courier_3', 'Ivan', 'Reparto'),
            ('demo_manager_1', 'Julia', 'Admin'),
            ('demo_manager_2', 'Kevin', 'Local'),
            ('demo_manager_3', 'Laura', 'Mesa'),
        ]:
            user = User.objects.create_user(
                username=username,
                password='demo12345',
                email=f'{username}@example.com',
                first_name=first_name,
                last_name=last_name,
            )
            users[username] = user

        roles = {
            'demo_consumer_1': Profile.Role.CONSUMER,
            'demo_consumer_2': Profile.Role.CONSUMER,
            'demo_consumer_3': Profile.Role.CONSUMER,
            'demo_producer_1': Profile.Role.PRODUCER,
            'demo_producer_2': Profile.Role.PRODUCER,
            'demo_producer_3': Profile.Role.PRODUCER,
            'demo_courier_1': Profile.Role.COURIER,
            'demo_courier_2': Profile.Role.COURIER,
            'demo_courier_3': Profile.Role.COURIER,
            'demo_manager_1': Profile.Role.WAREHOUSE_MANAGER,
            'demo_manager_2': Profile.Role.WAREHOUSE_MANAGER,
            'demo_manager_3': Profile.Role.WAREHOUSE_MANAGER,
        }

        profiles = {}
        for index, (username, role) in enumerate(roles.items(), start=1):
            profile = Profile(
                user=users[username],
                role=role,
                phone=f'+549110000{index:04d}',
                avatar=f'https://example.com/avatars/{username}.png',
            )
            self._save(profile)
            profiles[username] = profile

        addresses = {}
        address_rows = [
            ('demo_consumer_1', 'Av. Corrientes', '1234', 'CABA', 'Buenos Aires'),
            ('demo_consumer_2', 'San Martin', '845', 'La Plata', 'Buenos Aires'),
            ('demo_consumer_3', 'Belgrano', '220', 'Rosario', 'Santa Fe'),
            ('demo_producer_1', 'Ruta 8 Km', '71', 'Pergamino', 'Buenos Aires'),
            ('demo_producer_2', 'Camino Rural', '15', 'Rafaela', 'Santa Fe'),
            ('demo_producer_3', 'Ruta 12 Km', '9', 'Parana', 'Entre Rios'),
            ('demo_courier_1', 'Lavalle', '502', 'CABA', 'Buenos Aires'),
            ('demo_courier_2', 'Pellegrini', '340', 'Rosario', 'Santa Fe'),
            ('demo_courier_3', 'Mitre', '718', 'Cordoba', 'Cordoba'),
            ('demo_manager_1', 'Gurruchaga', '1500', 'CABA', 'Buenos Aires'),
            ('demo_manager_2', 'Guemes', '777', 'Mar del Plata', 'Buenos Aires'),
            ('demo_manager_3', 'Colon', '999', 'Cordoba', 'Cordoba'),
        ]
        for index, (username, street, number, city, province) in enumerate(address_rows, start=1):
            address = Address(
                owner=users[username],
                street=street,
                number=number,
                city=city,
                province=province,
                postal_code=f'D{index:04d}',
                lat=Decimal('-34.600000') + Decimal(index) / Decimal('1000'),
                lng=Decimal('-58.380000') - Decimal(index) / Decimal('1000'),
                is_default=True,
            )
            self._save(address)
            addresses[username] = address

        for username, profile in profiles.items():
            profile.default_address = addresses[username]
            self._save(profile)

        producers = []
        for username, business_name, tax_id in [
            ('demo_producer_1', 'Huerta Norte', 'DEMO-TAX-001'),
            ('demo_producer_2', 'Campo Claro', 'DEMO-TAX-002'),
            ('demo_producer_3', 'Verdes del Litoral', 'DEMO-TAX-003'),
        ]:
            producer = Producer(
                profile=profiles[username],
                business_name=business_name,
                tax_id=tax_id,
                address=addresses[username],
                description='Demo producer for admin exploration.',
            )
            self._save(producer)
            producers.append(producer)

        products = []
        product_rows = [
            (producers[0], 'Tomatoes', 'Fresh round tomatoes', Decimal('1200.00'), Product.Unit.KG),
            (producers[0], 'Lettuce Box', 'Mixed green lettuce', Decimal('8500.00'), Product.Unit.BOX),
            (producers[1], 'Potatoes', 'Washed potatoes', Decimal('700.00'), Product.Unit.KG),
            (producers[1], 'Carrot Box', 'Organic carrots', Decimal('6400.00'), Product.Unit.BOX),
            (producers[2], 'Honey Jar', 'Wildflower honey', Decimal('3200.00'), Product.Unit.UNIT),
            (producers[2], 'Orange Bag', 'Juicy oranges', Decimal('2100.00'), Product.Unit.KG),
        ]
        for producer, name, description, price, unit in product_rows:
            product = Product(producer=producer, name=name, description=description, price=price, unit=unit)
            self._save(product)
            products.append(product)

        warehouses = []
        for producer, name in [
            (producers[0], 'North Storage'),
            (producers[1], 'Central Barn'),
            (producers[2], 'River Depot'),
        ]:
            warehouse = Warehouse(producer=producer, name=name, address=producer.address)
            self._save(warehouse)
            warehouses.append(warehouse)

        inventory_rows = [
            (warehouses[0], products[0], Decimal('180.00')),
            (warehouses[0], products[1], Decimal('25.00')),
            (warehouses[1], products[2], Decimal('320.00')),
            (warehouses[1], products[3], Decimal('40.00')),
            (warehouses[2], products[4], Decimal('95.00')),
            (warehouses[2], products[5], Decimal('210.00')),
        ]
        for warehouse, product, quantity in inventory_rows:
            self._save(InventoryItem(warehouse=warehouse, product=product, quantity=quantity))

        restaurants = []
        restaurant_rows = [
            ('demo_manager_1', 'Demo Bistro', 'Comfort food and daily specials.'),
            ('demo_manager_2', 'Demo Pizza Club', 'Pizzas, empanadas, and drinks.'),
            ('demo_manager_3', 'Demo Vegan Bowl', 'Fresh plant-based bowls.'),
        ]
        for username, name, description in restaurant_rows:
            restaurant = Restaurant(owner=users[username], name=name, description=description, address=addresses[username])
            self._save(restaurant)
            restaurants.append(restaurant)

        restaurant_products = []
        menu_rows = [
            (restaurants[0], 'Burger Combo', 'Burger with fries', Decimal('9500.00')),
            (restaurants[0], 'Caesar Salad', 'Classic salad', Decimal('7200.00')),
            (restaurants[1], 'Mozzarella Pizza', 'Large pizza', Decimal('11000.00')),
            (restaurants[1], 'Empanada Dozen', 'Mixed empanadas', Decimal('9800.00')),
            (restaurants[2], 'Quinoa Bowl', 'Vegetables and quinoa', Decimal('8700.00')),
            (restaurants[2], 'Vegan Wrap', 'Grilled vegetable wrap', Decimal('7600.00')),
        ]
        for restaurant, name, description, price in menu_rows:
            menu_item = RestaurantProduct(restaurant=restaurant, name=name, description=description, price=price)
            self._save(menu_item)
            restaurant_products.append(menu_item)

        couriers = []
        courier_rows = [
            ('demo_courier_1', Courier.Vehicle.BIKE, '', True, 'CABA'),
            ('demo_courier_2', Courier.Vehicle.MOTORCYCLE, 'DEM123', True, 'Rosario'),
            ('demo_courier_3', Courier.Vehicle.CAR, 'DEM456', False, 'Cordoba'),
        ]
        for username, vehicle_type, license_plate, is_available, service_area in courier_rows:
            courier = Courier(
                profile=profiles[username],
                vehicle_type=vehicle_type,
                license_plate=license_plate,
                is_available=is_available,
                service_area=service_area,
            )
            self._save(courier)
            couriers.append(courier)

        restaurant_orders = [
            (users['demo_consumer_1'], addresses['demo_consumer_1'], Order.Status.DELIVERED, [(restaurant_products[0], Decimal('1.00')), (restaurant_products[1], Decimal('1.00'))]),
            (users['demo_consumer_2'], addresses['demo_consumer_2'], Order.Status.IN_DELIVERY, [(restaurant_products[2], Decimal('2.00'))]),
            (users['demo_consumer_3'], addresses['demo_consumer_3'], Order.Status.CONFIRMED, [(restaurant_products[4], Decimal('1.00')), (restaurant_products[5], Decimal('1.00'))]),
        ]
        agro_orders = [
            (users['demo_consumer_1'], addresses['demo_consumer_1'], Order.Status.CONFIRMED, [(products[0], Decimal('3.00')), (products[2], Decimal('5.00'))]),
            (users['demo_consumer_2'], addresses['demo_consumer_2'], Order.Status.PENDING, [(products[4], Decimal('2.00'))]),
            (users['demo_consumer_3'], addresses['demo_consumer_3'], Order.Status.DELIVERED, [(products[5], Decimal('4.00'))]),
        ]

        orders = []
        for consumer, delivery_address, status, items in restaurant_orders:
            order = self._create_order(consumer, delivery_address, Order.Mode.RESTAURANT, status, items)
            orders.append(order)
        for consumer, delivery_address, status, items in agro_orders:
            order = self._create_order(consumer, delivery_address, Order.Mode.AGRO, status, items)
            orders.append(order)

        payment_rows = [
            (orders[0], Payment.Method.CARD, Payment.Status.APPROVED),
            (orders[1], Payment.Method.CASH, Payment.Status.PENDING),
            (orders[2], Payment.Method.SIMULATED, Payment.Status.APPROVED),
            (orders[3], Payment.Method.TRANSFER, Payment.Status.APPROVED),
            (orders[4], Payment.Method.CARD, Payment.Status.PENDING),
            (orders[5], Payment.Method.SIMULATED, Payment.Status.APPROVED),
        ]
        for order, method, status in payment_rows:
            self._save(Payment(order=order, method=method, amount=order.total, status=status))

        now = timezone.now()
        delivery_rows = [
            (orders[0], couriers[0], Delivery.Status.DELIVERED, now - timezone.timedelta(hours=2), now - timezone.timedelta(hours=1)),
            (orders[1], couriers[1], Delivery.Status.IN_TRANSIT, now - timezone.timedelta(minutes=35), None),
            (orders[2], couriers[2], Delivery.Status.PENDING, None, None),
        ]
        for order, courier, status, picked_at, delivered_at in delivery_rows:
            self._save(Delivery(order=order, courier=courier, status=status, picked_at=picked_at, delivered_at=delivered_at))

        notification_rows = [
            (users['demo_consumer_1'], Notification.Type.ORDER, 'Your restaurant order was delivered.', True),
            (users['demo_consumer_2'], Notification.Type.DELIVERY, 'Your courier is on the way.', False),
            (users['demo_consumer_3'], Notification.Type.PAYMENT, 'Payment approved for your order.', False),
            (users['demo_producer_1'], Notification.Type.ORDER, 'New agro order received.', False),
            (users['demo_manager_1'], Notification.Type.SYSTEM, 'Demo restaurant is active.', True),
        ]
        for user, notification_type, message, is_read in notification_rows:
            self._save(Notification(user=user, type=notification_type, message=message, is_read=is_read))

        return {
            'Profile': Profile.objects.filter(user__username__startswith=DEMO_PREFIX).count(),
            'Address': Address.objects.filter(owner__username__startswith=DEMO_PREFIX).count(),
            'Order': Order.objects.filter(consumer__username__startswith=DEMO_PREFIX).count(),
            'OrderItem': OrderItem.objects.filter(order__consumer__username__startswith=DEMO_PREFIX).count(),
            'Payment': Payment.objects.filter(order__consumer__username__startswith=DEMO_PREFIX).count(),
            'Notification': Notification.objects.filter(user__username__startswith=DEMO_PREFIX).count(),
            'Restaurant': Restaurant.objects.filter(owner__username__startswith=DEMO_PREFIX).count(),
            'RestaurantProduct': RestaurantProduct.objects.filter(restaurant__owner__username__startswith=DEMO_PREFIX).count(),
            'Courier': Courier.objects.filter(profile__user__username__startswith=DEMO_PREFIX).count(),
            'Delivery': Delivery.objects.filter(order__consumer__username__startswith=DEMO_PREFIX).count(),
            'Producer': Producer.objects.filter(profile__user__username__startswith=DEMO_PREFIX).count(),
            'Product': Product.objects.filter(producer__profile__user__username__startswith=DEMO_PREFIX).count(),
            'Warehouse': Warehouse.objects.filter(producer__profile__user__username__startswith=DEMO_PREFIX).count(),
            'InventoryItem': InventoryItem.objects.filter(warehouse__producer__profile__user__username__startswith=DEMO_PREFIX).count(),
        }

    def _create_order(self, consumer, delivery_address, mode, status, items):
        total = sum((product.price * quantity for product, quantity in items), Decimal('0.00')).quantize(Decimal('0.01'))
        order = Order(consumer=consumer, mode=mode, status=status, delivery_address=delivery_address, total=total)
        self._save(order)

        for product, quantity in items:
            item_kwargs = {
                'order': order,
                'quantity': quantity,
                'unit_price': product.price,
            }
            if mode == Order.Mode.RESTAURANT:
                item_kwargs['restaurant_product'] = product
            else:
                item_kwargs['agro_product'] = product
            self._save(OrderItem(**item_kwargs))

        return order

    def _save(self, instance):
        instance.full_clean()
        instance.save()
        return instance
