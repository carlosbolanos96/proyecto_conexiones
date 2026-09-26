from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile
from locations.models import Address


class ProfileValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='consumer', password='testpass123')
        cls.other_user = User.objects.create_user(username='other-consumer', password='testpass123')
        cls.user_address = Address.objects.create(
            owner=cls.user,
            street='Main',
            number='123',
            city='CABA',
            province='Buenos Aires',
        )
        cls.other_address = Address.objects.create(
            owner=cls.other_user,
            street='Side',
            number='456',
            city='La Plata',
            province='Buenos Aires',
        )

    def test_default_address_must_belong_to_profile_user(self):
        profile = Profile(
            user=self.user,
            role=Profile.Role.CONSUMER,
            default_address=self.other_address,
        )

        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()

        self.assertIn('default_address', cm.exception.error_dict)

    def test_objects_create_does_not_run_model_clean(self):
        profile = Profile.objects.create(
            user=self.user,
            role=Profile.Role.CONSUMER,
            default_address=self.other_address,
        )

        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()

        self.assertIn('default_address', cm.exception.error_dict)

    def test_default_address_owned_by_user_passes_validation(self):
        profile = Profile(
            user=self.user,
            role=Profile.Role.CONSUMER,
            default_address=self.user_address,
        )

        profile.full_clean()
