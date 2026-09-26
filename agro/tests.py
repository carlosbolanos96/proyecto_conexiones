from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile
from agro.models import Producer
from locations.models import Address


class ProducerValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.consumer_user = User.objects.create_user(username='consumer', password='testpass123')
        cls.producer_user = User.objects.create_user(username='producer', password='testpass123')
        cls.consumer_profile = Profile.objects.create(user=cls.consumer_user, role=Profile.Role.CONSUMER)
        cls.producer_profile = Profile.objects.create(user=cls.producer_user, role=Profile.Role.PRODUCER)
        cls.consumer_address = Address.objects.create(
            owner=cls.consumer_user,
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

    def test_profile_must_have_producer_role(self):
        producer = Producer(
            profile=self.consumer_profile,
            business_name='Invalid Farm',
            tax_id='TAX-AGRO-001',
            address=self.consumer_address,
        )

        with self.assertRaises(ValidationError) as cm:
            producer.full_clean()

        self.assertIn('profile', cm.exception.error_dict)

    def test_profile_with_producer_role_passes_validation(self):
        producer = Producer(
            profile=self.producer_profile,
            business_name='Valid Farm',
            tax_id='TAX-AGRO-002',
            address=self.producer_address,
        )

        producer.full_clean()
