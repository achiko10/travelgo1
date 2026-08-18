from django.test import TestCase
from django.contrib.auth import get_user_model
from maps.models import PointOfInterest, CheckIn
from inventory.models import Badge, Skin, UserInventory
from social.models import Friendship
from django.db.utils import IntegrityError

User = get_user_model()

class UserSecurityTests(TestCase):
    def test_user_creation_username_unique(self):
        u1 = User.objects.create_user(email="test@travelgo.ge", password="password123")
        u2 = User.objects.create_user(email="test@travelgo.ge2", password="password123")
        self.assertNotEqual(u1.username, u2.username)

    def test_referral_code_auto_generated(self):
        u = User.objects.create_user(email="ref@travelgo.ge", password="password123")
        self.assertIsNotNone(u.referral_code)
        self.assertEqual(len(u.referral_code), 6)

class InventoryConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="inv@travelgo.ge", password="password123")
        self.badge = Badge.objects.create(name="Tbilisi Explorer", coin_price=100)
        self.skin = Skin.objects.create(name="Adjaran Chokha", coin_price=200)

    def test_unique_user_badge(self):
        UserInventory.objects.create(user=self.user, badge=self.badge)
        with self.assertRaises(IntegrityError):
            UserInventory.objects.create(user=self.user, badge=self.badge)

    def test_unique_user_skin(self):
        UserInventory.objects.create(user=self.user, skin=self.skin)
        with self.assertRaises(IntegrityError):
            UserInventory.objects.create(user=self.user, skin=self.skin)

class SocialConstraintTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(email="u1@travelgo.ge", password="password123")
        self.u2 = User.objects.create_user(email="u2@travelgo.ge", password="password123")

    def test_prevent_self_friendship(self):
        with self.assertRaises(IntegrityError):
            Friendship.objects.create(from_user=self.u1, to_user=self.u1)

    def test_unique_friendship_direction(self):
        Friendship.objects.create(from_user=self.u1, to_user=self.u2)
        with self.assertRaises(IntegrityError):
            Friendship.objects.create(from_user=self.u1, to_user=self.u2)
