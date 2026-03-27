from django.db import models
from django.conf import settings

class Badge(models.Model):
    RARITY_CHOICES = (
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/', null=True, blank=True)
    rarity = models.CharField(max_length=50, choices=RARITY_CHOICES, default='common')
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"

class Skin(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='skins/', null=True, blank=True)
    region_unlock = models.CharField(max_length=100, blank=True, help_text="მაგ: aჭარა, სვანეთი (Adjara, Svaneti)")
    
    def __str__(self):
        return self.name

class UserInventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, null=True, blank=True)
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, null=True, blank=True)
    date_unlocked = models.DateTimeField(auto_now_add=True)
    location_unlocked_from = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        item = self.badge.name if self.badge else (self.skin.name if self.skin else "Item")
        return f"{self.user.email} -> {item}"
