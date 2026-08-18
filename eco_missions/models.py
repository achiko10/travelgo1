from django.db import models
from django.conf import settings


class Landmark(models.Model):
    """
    Tbilisi landmarks (historical + modern).
    """
    CATEGORY_CHOICES = (
        ('historical', 'Historical'),
        ('modern', 'Modern'),
    )

    poi = models.ForeignKey(
        'maps.PointOfInterest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='landmarks',
        verbose_name="დაკავშირებული POI"
    )
    name_ka = models.CharField(max_length=200, verbose_name="Name (KA)")
    name_en = models.CharField(max_length=200, blank=True, verbose_name="Name (EN)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='historical')
    address = models.CharField(max_length=300, verbose_name="Address")
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)

    class Meta:
        verbose_name = "Landmark"
        verbose_name_plural = "Landmarks"
        ordering = ['name_ka']

    def __str__(self):
        return f"{self.name_ka} ({self.category})"


class EcoMission(models.Model):
    """
    Eco-missions with geofence, requirements, rewards, and campaign dates.
    """
    mission_id = models.CharField(max_length=100, unique=True, verbose_name="Mission ID")
    title = models.CharField(max_length=300, verbose_name="Title (KA)")
    title_en = models.CharField(max_length=300, blank=True, verbose_name="Title (EN)")
    location_name = models.CharField(max_length=300, verbose_name="Location Name")
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    geofence_radius_m = models.PositiveIntegerField(null=True, blank=True, verbose_name="Geofence Radius (m)")
    task_description = models.TextField(verbose_name="Task Description (KA)")
    task_description_en = models.TextField(blank=True, verbose_name="Task Description (EN)")
    ar_object = models.CharField(max_length=200, blank=True, null=True, verbose_name="AR Object Filename")

    # Requirements stored as JSON
    requirements = models.JSONField(default=dict, blank=True, verbose_name="Requirements")

    # Rewards
    reward_skin = models.CharField(max_length=200, blank=True, verbose_name="Reward Skin")
    reward_badge = models.CharField(max_length=200, blank=True, verbose_name="Reward Badge")
    reward_xp = models.PositiveIntegerField(default=0, verbose_name="Reward XP")
    reward_points = models.PositiveIntegerField(default=0, verbose_name="Reward Points")
    reward_discount = models.CharField(max_length=200, blank=True, null=True, verbose_name="Reward Discount")
    reward_notes = models.TextField(blank=True, verbose_name="Reward Notes")

    # UI Buttons
    buttons = models.JSONField(default=list, blank=True, verbose_name="Action Buttons")

    # Campaign dates (optional)
    campaign_start_date = models.DateField(null=True, blank=True, verbose_name="Campaign Start")
    campaign_end_date = models.DateField(null=True, blank=True, verbose_name="Campaign End")

    # Extra notes for internal use
    notes = models.TextField(blank=True, verbose_name="Internal Notes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Eco Mission"
        verbose_name_plural = "Eco Missions"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_campaign_active(self):
        """Check if campaign mission is currently active."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.campaign_start_date and self.campaign_end_date:
            return self.campaign_start_date <= today <= self.campaign_end_date
        return True  # Non-campaign missions are always active


class WasteType(models.Model):
    """
    QR code waste types for cleanup missions (e.g. Turtle Lake).
    """
    TYPE_CHOICES = (
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('other', 'Other'),
    )

    mission = models.ForeignKey(EcoMission, on_delete=models.CASCADE, related_name='waste_types')
    waste_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    qr_code_value = models.CharField(max_length=100, unique=True, verbose_name="QR Code Value")

    class Meta:
        verbose_name = "Waste Type QR"
        verbose_name_plural = "Waste Type QRs"

    def __str__(self):
        return f"{self.mission.mission_id} - {self.waste_type} ({self.qr_code_value})"


class UserMissionProgress(models.Model):
    """
    Tracks individual user progress on eco-missions.
    """
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_progress')
    mission = models.ForeignKey(EcoMission, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    qr_scanned_count = models.PositiveIntegerField(default=0)
    photo_uploaded = models.BooleanField(default=False)
    gps_points_visited = models.JSONField(default=list, blank=True, verbose_name="GPS Points Visited")
    xp_earned = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Mission Progress"
        verbose_name_plural = "User Mission Progress"
        unique_together = ('user', 'mission')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.mission.title} ({self.status})"
