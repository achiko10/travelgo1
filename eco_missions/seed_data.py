"""
Seed script for eco_missions app.
Run: python manage.py shell < eco_missions/seed_data.py
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelgo_core.settings')

# Setup Django if not already
if not hasattr(django, '_setup_done'):
    django.setup()

from eco_missions.models import Landmark, EcoMission, WasteType

# ============================================================
# 1. LANDMARKS (14 Tbilisi locations with real coordinates)
# ============================================================
landmarks_data = [
    {"name_ka": "Narikala Fortress", "name_en": "Narikala Fortress", "category": "historical", "address": "Narikala Fortress, Tbilisi", "latitude": 41.6875, "longitude": 44.8082},
    {"name_ka": "Abanotubani", "name_en": "Old Tbilisi (Abanotubani)", "category": "historical", "address": "Abanotubani, Tbilisi", "latitude": 41.6885, "longitude": 44.8108},
    {"name_ka": "Holy Trinity Cathedral", "name_en": "Holy Trinity Cathedral of Tbilisi", "category": "historical", "address": "Holy Trinity Cathedral of Tbilisi", "latitude": 41.6976, "longitude": 44.8059},
    {"name_ka": "Metekhi Cathedral", "name_en": "Metekhi Cathedral", "category": "historical", "address": "Metekhi Cathedral, Tbilisi", "latitude": 41.6912, "longitude": 44.8103},
    {"name_ka": "Anchiskhati Basilica", "name_en": "Anchiskhati Basilica", "category": "historical", "address": "Anchiskhati Basilica, Ioane Shavteli St, Tbilisi", "latitude": 41.6935, "longitude": 44.8065},
    {"name_ka": "Sioni Cathedral", "name_en": "Sioni Cathedral", "category": "historical", "address": "Sioni Cathedral, Sioni St, Tbilisi", "latitude": 41.6919, "longitude": 44.8087},
    {"name_ka": "Georgian National Museum", "name_en": "Georgian National Museum", "category": "historical", "address": "Georgian National Museum, 3 Shota Rustaveli Ave, Tbilisi", "latitude": 41.6974, "longitude": 44.7999},
    {"name_ka": "Bridge of Peace", "name_en": "The Bridge of Peace", "category": "modern", "address": "The Bridge of Peace, Tbilisi", "latitude": 41.6935, "longitude": 44.8088},
    {"name_ka": "Rike Park", "name_en": "Rike Park", "category": "modern", "address": "Rike Park, Tbilisi", "latitude": 41.6927, "longitude": 44.8102},
    {"name_ka": "Mtatsminda Park", "name_en": "Mtatsminda Park", "category": "modern", "address": "Mtatsminda Park, Tbilisi", "latitude": 41.6932, "longitude": 44.7851},
    {"name_ka": "Freedom Square", "name_en": "Freedom Square", "category": "modern", "address": "Freedom Square, Tbilisi", "latitude": 41.6941, "longitude": 44.8015},
    {"name_ka": "Rustaveli Avenue", "name_en": "Rustaveli Avenue", "category": "modern", "address": "Rustaveli Avenue, Tbilisi", "latitude": 41.7012, "longitude": 44.7935},
    {"name_ka": "Fabrika", "name_en": "Fabrika", "category": "modern", "address": "Fabrika, 8 Egnate Ninoshvili St, Tbilisi", "latitude": 41.7065, "longitude": 44.7929},
    {"name_ka": "Dry Bridge Market", "name_en": "Dry Bridge Market", "category": "modern", "address": "Dry Bridge Market, Tbilisi", "latitude": 41.6982, "longitude": 44.8028},
]

created_landmarks = 0
for lm in landmarks_data:
    obj, created = Landmark.objects.get_or_create(
        name_en=lm['name_en'],
        defaults=lm,
    )
    if created:
        created_landmarks += 1

print(f"Landmarks: {created_landmarks} created, {len(landmarks_data) - created_landmarks} already existed.")

# ============================================================
# 2. ECO MISSIONS (8 missions)
# ============================================================
missions_data = [
    {
        "mission_id": "turtle_lake_cleanup",
        "title": "Turtle Lake Cleanup",
        "title_en": "Clean up the Turtle Lake trail",
        "location_name": "Turtle Lake trail, Tbilisi",
        "latitude": 41.7059,
        "longitude": 44.7546,
        "geofence_radius_m": 200,
        "task_description": "Collect 5 types of waste and scan corresponding QR codes on the territory",
        "requirements": {"min_qr_scans": 3, "photo_upload_alternative": True},
        "reward_skin": "turtle_guardian_skin_001",
        "reward_badge": "Eco Hero Level 1",
        "reward_xp": 10,
        "reward_points": 10,
        "buttons": ["Start Mission", "Scan QR", "Upload Photo"],
        "campaign_start_date": "2026-07-10",
        "campaign_end_date": "2026-09-30",
    },
    {
        "mission_id": "mtatsminda_water_plant",
        "title": "Water a Plant at Mtatsminda Park",
        "title_en": "Water a plant in Mtatsminda Park",
        "location_name": "Mtatsminda Park inner territory",
        "latitude": 41.6932,
        "longitude": 44.7851,
        "geofence_radius_m": 100,
        "task_description": "Scan the AR plant and activate the watering animation",
        "ar_object": "animated_flower_v01.glb",
        "requirements": {"ar_interaction": "tap_or_button_water"},
        "reward_skin": "flower_patch_skin_03",
        "reward_badge": "Plant Protector",
        "reward_xp": 8,
        "reward_points": 0,
        "buttons": ["Start Mission", "Revive Plant (AR)", "Add to My Garden"],
    },
    {
        "mission_id": "lagodekhi_trail",
        "title": "Discover Lagodekhi Trail",
        "title_en": "Discover Lagodekhi Trail",
        "location_name": "Lagodekhi Protected Area",
        "latitude": 41.8240,
        "longitude": 46.2753,
        "geofence_radius_m": None,
        "task_description": "Walk 3km trail, mark 3 nature spots and collect artifacts",
        "requirements": {"min_gps_points": 3},
        "reward_skin": "explorer_backpack_skin",
        "reward_badge": "Eco Scout",
        "reward_xp": 15,
        "reward_points": 0,
        "buttons": ["Start Route", "Mark Locations", "Add Artifact"],
    },
    {
        "mission_id": "batumi_boulevard_cleanup",
        "title": "Batumi Cleanup Challenge",
        "title_en": "Batumi Boulevard Cleanup Challenge",
        "location_name": "Batumi Boulevard",
        "latitude": 41.6506,
        "longitude": 41.6370,
        "geofence_radius_m": None,
        "task_description": "Participate in a cleanup activity, upload a selfie or environmental photo",
        "requirements": {"geo_tagged_photo_upload": True},
        "reward_xp": 0,
        "reward_points": 0,
        "reward_discount": "Partner cafe",
        "reward_notes": "Score board with cleanup progress",
        "buttons": ["Start Mission", "Upload Photo"],
    },
    {
        "mission_id": "deda_ena_plant_tree",
        "title": "Plant Life - Deda Ena Garden",
        "title_en": "Plant a tree at Deda Ena Garden",
        "location_name": "Deda Ena Garden, Tbilisi",
        "latitude": 41.6994,
        "longitude": 44.8057,
        "geofence_radius_m": None,
        "task_description": "Participate in a real or AR tree planting event",
        "requirements": {"activation_type": "qr_or_ar"},
        "reward_badge": "Green Soul",
        "reward_xp": 5,
        "reward_points": 0,
        "reward_notes": "Virtual tree added to user profile",
        "buttons": ["Start Mission", "Scan QR/AR"],
    },
    {
        "mission_id": "botanical_garden_find_5",
        "title": "Plant Jewelry",
        "title_en": "Plant Jewelry - Botanical Garden",
        "location_name": "Tbilisi Botanical Garden",
        "latitude": 41.6825,
        "longitude": 44.8078,
        "geofence_radius_m": None,
        "task_description": "Find and scan 5 unique plants using the AR game",
        "requirements": {"ar_objects_count": 5},
        "reward_xp": 12,
        "reward_points": 5,
        "reward_notes": "Visual artifacts + bonus points, each scan adds to passport",
        "buttons": ["Start Mission", "Scan Plant (AR)"],
    },
    {
        "mission_id": "okatse_selfie",
        "title": "Nature By Your Side - Okatse",
        "title_en": "Nature selfie at Okatse Canyon",
        "location_name": "Okatse Canyon",
        "latitude": 42.5141,
        "longitude": 42.3303,
        "geofence_radius_m": None,
        "task_description": "Take a selfie with a natural background and upload to the app",
        "requirements": {"camera_active_only_on_location": True},
        "reward_xp": 8,
        "reward_points": 0,
        "reward_notes": "Leaderboard points + photo in passport, AR frame Green Explorer",
        "buttons": ["Start Mission", "Take Selfie"],
    },
    {
        "mission_id": "mestia_eco_culture",
        "title": "Eco Culture Trail - Mestia",
        "title_en": "Eco Culture Trail in Mestia",
        "location_name": "Mestia Eco Trail",
        "latitude": 43.0451,
        "longitude": 42.7282,
        "geofence_radius_m": None,
        "task_description": "Learn and scan 3 local eco-tradition info cards",
        "requirements": {"min_ar_card_scans": 3},
        "reward_skin": "svaneti_skin",
        "reward_badge": "Culture Badge",
        "reward_xp": 10,
        "reward_points": 0,
        "reward_notes": "Culture badge earned",
        "buttons": ["Start Mission", "Scan Info Card"],
    },
]

created_missions = 0
for m in missions_data:
    # Extract campaign dates
    start = m.pop('campaign_start_date', None)
    end = m.pop('campaign_end_date', None)
    if start:
        m['campaign_start_date'] = start
    if end:
        m['campaign_end_date'] = end

    obj, created = EcoMission.objects.get_or_create(
        mission_id=m['mission_id'],
        defaults=m,
    )
    if created:
        created_missions += 1

print(f"Eco Missions: {created_missions} created, {len(missions_data) - created_missions} already existed.")

# ============================================================
# 3. WASTE TYPES for Turtle Lake mission
# ============================================================
turtle_mission = EcoMission.objects.filter(mission_id='turtle_lake_cleanup').first()
if turtle_mission:
    waste_types = [
        {"waste_type": "plastic", "qr_code_value": "TL-PLASTIC-001"},
        {"waste_type": "paper", "qr_code_value": "TL-PAPER-001"},
        {"waste_type": "glass", "qr_code_value": "TL-GLASS-001"},
        {"waste_type": "metal", "qr_code_value": "TL-METAL-001"},
        {"waste_type": "other", "qr_code_value": "TL-OTHER-001"},
    ]
    created_wt = 0
    for wt in waste_types:
        obj, created = WasteType.objects.get_or_create(
            mission=turtle_mission,
            qr_code_value=wt['qr_code_value'],
            defaults=wt,
        )
        if created:
            created_wt += 1
    print(f"Waste Types: {created_wt} created for Turtle Lake mission.")
else:
    print("WARNING: Turtle Lake mission not found, skipping waste types.")

print("Seed complete!")
