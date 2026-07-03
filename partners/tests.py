from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Partner

class PartnersAPITests(APITestCase):
    def setUp(self):
        self.category_hotel = Category.objects.create(name="Hotels", icon_name="hotel")
        self.category_food = Category.objects.create(name="Restaurants", icon_name="restaurant")
        
        self.partner_1 = Partner.objects.create(
            name="Test Hotel",
            category=self.category_hotel,
            location_address="Tbilisi, Georgia",
            offer_percentage=10,
            description="10% off stay"
        )
        self.partner_2 = Partner.objects.create(
            name="Test Cafe",
            category=self.category_food,
            location_address="Tbilisi, Georgia",
            offer_percentage=15,
            description="15% off food"
        )

    def test_category_list(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.statusCode if hasattr(response, 'statusCode') else response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_partner_list_all(self):
        url = reverse('partner-list')
        response = self.client.get(url)
        self.assertEqual(response.statusCode if hasattr(response, 'statusCode') else response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_partner_list_filter(self):
        url = reverse('partner-list')
        response = self.client.get(url, {'category': self.category_hotel.id})
        self.assertEqual(response.statusCode if hasattr(response, 'statusCode') else response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Hotel")
