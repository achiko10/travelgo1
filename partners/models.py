from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="კატეგორია (სასტუმრო, კაფე, Dental)")
    icon_name = models.CharField(max_length=50, blank=True, help_text="Flutter Icon Name")
    
    def __str__(self):
        return self.name

class Partner(models.Model):
    name = models.CharField(max_length=150, verbose_name="პარტნიორის დასახელება")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='partners')
    logo = models.ImageField(upload_to='partners_logos/', blank=True, null=True)
    location_address = models.CharField(max_length=255, verbose_name="მისამართი")
    
    latitude = models.FloatField(default=41.7151)
    longitude = models.FloatField(default=44.8271)
    
    offer_percentage = models.PositiveIntegerField(default=5, verbose_name="ფასდაკლების % (ან ბონუსი)")
    description = models.TextField(verbose_name="შეთავაზების დეტალები", blank=True)
    terms_and_conditions = models.TextField(verbose_name="წესები და პირობები", blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
