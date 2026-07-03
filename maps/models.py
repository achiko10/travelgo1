from django.db import models
from django.conf import settings

# შენიშვნა: GeoDjango/GDAL არ გამოიყენება — GDAL Windows/PythonAnywhere-ზე არ არის.
# კოორდინატები ინახება Float ველებში (latitude/longitude).
# Haversine ფორმულა (maps/utils.py) ახდენს ყველა geo-გამოთვლას.


class PointOfInterest(models.Model):
    POI_TYPES = (
        ('historical', 'ისტორიული'),
        ('tourist', 'ტურისტული ადგილი'),
        ('museum', 'მუზეუმი'),
        ('park', 'პარკი'),
        ('food', 'კვების ობიექტი'),
        ('entertainment', 'გასართობი ადგილი'),
        ('partner', 'პარტნიორი ბიზნესი'),
    )

    # ── ძირითადი ველები (ქართული — default) ──────────────────────────────────
    name = models.CharField(max_length=200, verbose_name="დასახელება (KA)")
    description = models.TextField(verbose_name="აღწერა (KA)")
    open_hours = models.CharField(max_length=100, blank=True, verbose_name="სამუშაო საათები (KA)")

    # ── ინგლისური ვერსია ──────────────────────────────────────────────────────
    name_en = models.CharField(max_length=200, blank=True, verbose_name="Name (EN)")
    description_en = models.TextField(blank=True, verbose_name="Description (EN)")
    open_hours_en = models.CharField(max_length=100, blank=True, verbose_name="Open Hours (EN)")

    # ── მედია ─────────────────────────────────────────────────────────────────
    photo = models.ImageField(upload_to='pois/', blank=True, null=True, verbose_name="ფოტო")
    audio_guide = models.FileField(upload_to='audio/', blank=True, null=True, verbose_name="აუდიო გიდი (KA)")
    audio_guide_en = models.FileField(upload_to='audio/', blank=True, null=True, verbose_name="Audio Guide (EN)")

    poi_type = models.CharField(max_length=50, choices=POI_TYPES, verbose_name="ლოკაციის ტიპი")

    # ── კოორდინატები ──────────────────────────────────────────────────────────
    latitude = models.FloatField(verbose_name="Latitude (Y)", default=41.7151)
    longitude = models.FloatField(verbose_name="Longitude (X)", default=44.8271)

    base_xp = models.PositiveIntegerField(default=50, verbose_name="გასაცემი XP ქულები")
    reward_badge_name = models.CharField(
        max_length=100, blank=True,
        help_text="რა Skin/Badge შეიძლება მოგცეს (XP გარდა)"
    )
    google_maps_link = models.URLField(blank=True, verbose_name="Google Maps ლინკი")

    def __str__(self):
        return f"{self.name} ({self.get_poi_type_display()})"


class RedZone(models.Model):
    """თაღლითების ზონა — Flutter Map-ზე წითლად გამოჩნდება"""
    name = models.CharField(max_length=100, verbose_name="ზონის სახელი (KA)")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Zone Name (EN)")
    latitude = models.FloatField(default=41.7151)
    longitude = models.FloatField(default=44.8271)
    radius_meters = models.FloatField(default=100.0, verbose_name="რადიუსი მეტრებში")

    def __str__(self):
        return f"RED ZONE: {self.name}"


class CheckIn(models.Model):
    """Check-in ჩანაწერი — unique_together: ერთ ლოკაციაში ერთხელ"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins')
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE, related_name='checkins')
    timestamp = models.DateTimeField(auto_now_add=True)
    awarded_xp = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'poi')
        verbose_name = "ჩექინი (Check-in)"

    def __str__(self):
        return f"{self.user.email} -> {self.poi.name}"
