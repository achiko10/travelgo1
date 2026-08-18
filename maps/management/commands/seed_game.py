import random
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser
from maps.models import PointOfInterest
from inventory.models import Badge, Skin, UserInventory
from quests.models import QuizQuestion, DailyQuest
from partners.models import Partner, Category, DiscountCoupon
from eco_missions.models import EcoMission, WasteType
from social.models import Friendship, FriendActivity, ChallengeInvite

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed TravelGo database with rich playable game data (POIs, Shop, Quizzes, Partners, Social)'

    def handle(self, *args, **options):
        self.stdout.write("Starting TravelGo Master Game Data Seeding...")

        # 1. SEED SHOP ITEMS (Badges & Skins)
        self.stdout.write("1. Seeding Shop Items (Badges & Skins)...")
        badges = [
            {"name": "Eco Guardian Badge", "description": "Awarded for eco cleanup missions", "coin_price": 50, "is_for_sale": True, "rarity": "rare"},
            {"name": "Explorer Supreme", "description": "Visited over 10 historic locations", "coin_price": 100, "is_for_sale": True, "rarity": "epic"},
            {"name": "Narikala Conqueror", "description": "Checked in at Narikala Fortress", "coin_price": 75, "is_for_sale": True, "rarity": "common"},
            {"name": "Master Navigator", "description": "Completed 5 PvP Challenges", "coin_price": 150, "is_for_sale": True, "rarity": "legendary"},
        ]
        skins = [
            {"name": "Georgian Chokha Special", "description": "Traditional royal Georgian national dress", "coin_price": 200, "is_for_sale": True},
            {"name": "Golden Knight Armor", "description": "Epic golden medieval armor", "coin_price": 350, "is_for_sale": True},
            {"name": "Cyberpunk Explorer", "description": "Futuristic cyberpunk travel jacket", "coin_price": 250, "is_for_sale": True},
            {"name": "Royal Crown", "description": "Golden King Vakhtang Gorgasali crown", "coin_price": 180, "is_for_sale": True},
        ]
        for bdata in badges:
            Badge.objects.get_or_create(name=bdata["name"], defaults=bdata)

        for sdata in skins:
            Skin.objects.get_or_create(name=sdata["name"], defaults=sdata)

        # 2. SEED USERS
        self.stdout.write("2. Seeding Test Users & Competitors...")
        test_users_data = [
            {"email": "giorgi@travelgo.ge", "username": "giorgi_traveler", "full_name": "Giorgi Beridze", "xp": 1450, "level": 4, "coins": 350},
            {"email": "nino@travelgo.ge", "username": "nino_adventurer", "full_name": "Nino Kapanadze", "xp": 2100, "level": 5, "coins": 500},
            {"email": "luka@travelgo.ge", "username": "luka_explorer", "full_name": "Luka Gelashvili", "xp": 980, "level": 3, "coins": 200},
            {"email": "ana@travelgo.ge", "username": "ana_georgia", "full_name": "Ana Maisuradze", "xp": 3200, "level": 7, "coins": 850},
        ]
        created_users = []
        for udata in test_users_data:
            user, created = CustomUser.objects.get_or_create(email=udata["email"], defaults={
                "username": udata["username"],
                "full_name": udata["full_name"],
                "xp": udata["xp"],
                "level": udata["level"],
                "coins": udata["coins"],
            })
            if created:
                user.set_password("password123")
                user.save()
            created_users.append(user)

        # Ensure demo user exists
        demo_user, _ = CustomUser.objects.get_or_create(email="testuser@travelgo.ge", defaults={
            "username": "demouser",
            "full_name": "Demo Player",
            "coins": 500,
            "xp": 300,
            "level": 2
        })
        if demo_user.pk and not demo_user.check_password("password123"):
            demo_user.set_password("password123")
            demo_user.save()

        # 3. SEED POIs ACROSS GEORGIA
        self.stdout.write("3. Seeding Points of Interest (POIs)...")
        pois_data = [
            {"name": "Narikala Fortress", "poi_type": "historical", "latitude": 41.6875, "longitude": 44.8082, "base_xp": 50, "description": "Dzveli Tbilisis istoriuli tsikhesimagre IV saukunidan."},
            {"name": "Holy Trinity Cathedral (Sameba)", "poi_type": "historical", "latitude": 41.6976, "longitude": 44.8059, "base_xp": 40, "description": "Sakartvelos martlmadidebeli eklesiis mtavari sakatedro tadzari."},
            {"name": "The Bridge of Peace", "poi_type": "tourist", "latitude": 41.6935, "longitude": 44.8088, "base_xp": 30, "description": "Tanamedrove shushis sapegmavlo khidi mtgvarze."},
            {"name": "Mtatsminda Park", "poi_type": "park", "latitude": 41.6932, "longitude": 44.7851, "base_xp": 45, "description": "Panoramuli parki da atraktsionebi mtatsmindis platoze."},
            {"name": "Old Tbilisi Sulfur Baths", "poi_type": "historical", "latitude": 41.6885, "longitude": 44.8108, "base_xp": 35, "description": "Abanotubani - gogirdis abanoebi."},
            {"name": "Jvari Monastery", "poi_type": "historical", "latitude": 41.8383, "longitude": 44.7333, "base_xp": 60, "description": "VI saukunis tadzari mtskhetashi."},
            {"name": "Svetitskhoveli Cathedral", "poi_type": "historical", "latitude": 41.8422, "longitude": 44.7208, "base_xp": 60, "description": "Sakartvelos sulieri tsentri da UNESCO memkvidreoba."},
            {"name": "Bagrati Cathedral (Kutaisi)", "poi_type": "historical", "latitude": 42.2772, "longitude": 42.7042, "base_xp": 50, "description": "XI saukunis tadzari qutaishi."},
            {"name": "Gelati Monastery", "poi_type": "historical", "latitude": 42.2964, "longitude": 42.7686, "base_xp": 60, "description": "Davit Agmasheneblis mier daarsebuli monasteri."},
            {"name": "Sighnaghi City of Love", "poi_type": "tourist", "latitude": 41.6167, "longitude": 45.9167, "base_xp": 55, "description": "Kakhetis tsikhe-qalaqi Alaznis velze."},
            {"name": "Batumi Boulevard", "poi_type": "park", "latitude": 41.6500, "longitude": 41.6333, "base_xp": 40, "description": "Shavi zghis sanapironi parki."},
            {"name": "Mestia Towers (Svaneti)", "poi_type": "historical", "latitude": 43.0447, "longitude": 42.7297, "base_xp": 70, "description": "Svanuri koshkebi da kavkasionis mtsvervalebi."},
        ]

        created_pois = []
        for pdata in pois_data:
            poi, _ = PointOfInterest.objects.get_or_create(name=pdata["name"], defaults=pdata)
            created_pois.append(poi)

        # 4. SEED QUIZZES & DAILY QUESTS FOR POIs
        self.stdout.write("4. Seeding Quizzes & Daily Quests for POIs...")
        for poi in created_pois:
            # Quiz
            QuizQuestion.objects.get_or_create(
                poi=poi,
                question=f"Romel saukuneshi aigo {poi.name}?",
                defaults={
                    "answer1": "IV-VI saukuneebi",
                    "answer2": "XI-XII saukuneebi",
                    "answer3": "XVIII saukune",
                    "answer4": "XX saukune",
                    "correct_index": 0
                }
            )
            # Daily Quest
            DailyQuest.objects.get_or_create(
                title=f"Visit {poi.name}",
                defaults={
                    "description": f"Go to {poi.name} and check in to earn extra XP!",
                    "reward_xp": 100,
                    "reward_coins": 50,
                    "target_poi": poi,
                    "date_active": date.today()
                }
            )

        # 5. SEED PARTNERS & COUPONS
        self.stdout.write("5. Seeding Partners & Discount Coupons...")
        cat_rest, _ = Category.objects.get_or_create(name="Restaurant", defaults={"icon_name": "utensils"})
        cat_wine, _ = Category.objects.get_or_create(name="Winery", defaults={"icon_name": "wine-glass"})
        cat_hotel, _ = Category.objects.get_or_create(name="Hotel & Cafe", defaults={"icon_name": "hotel"})

        partners_data = [
            {"name": "Chateau Mukhrani Winery", "category": cat_wine, "latitude": 41.9408, "longitude": 44.5786, "offer_percentage": 20, "description": "Royal estate and wine degustation in Kartli.", "location_address": "Mukhrani, Kartli"},
            {"name": "Barbarestan Restaurant", "category": cat_rest, "latitude": 41.7100, "longitude": 44.7950, "offer_percentage": 15, "description": "Authentic Georgian cuisine based on 19th-century recipes.", "location_address": "D. Aghmashenebeli Ave 132, Tbilisi"},
            {"name": "Fabrika Tbilisi", "category": cat_hotel, "latitude": 41.7065, "longitude": 44.7929, "offer_percentage": 10, "description": "Urban hotspot, hostel, and open-air cafes.", "location_address": "E. Ninoshvili St 8, Tbilisi"},
        ]
        for part_data in partners_data:
            partner, created = Partner.objects.get_or_create(name=part_data["name"], defaults=part_data)
            if not created:
                partner.offer_percentage = part_data["offer_percentage"]
                partner.save()
            DiscountCoupon.objects.get_or_create(
                partner=partner,
                defaults={
                    "discount_pct": 15,
                    "status": "active",
                    "valid_until": "2026-12-31"
                }
            )

        # 6. SEED SOCIAL FRIENDSHIPS & PVP CHALLENGE
        self.stdout.write("6. Seeding Friendships & PvP Challenges...")
        giorgi = created_users[0]
        nino = created_users[1]

        # Friendships
        Friendship.objects.get_or_create(from_user=demo_user, to_user=giorgi, defaults={"status": "accepted"})
        Friendship.objects.get_or_create(from_user=demo_user, to_user=nino, defaults={"status": "accepted"})

        # Social Feed Activities
        narikala_poi = created_pois[0]
        FriendActivity.objects.get_or_create(
            user=giorgi,
            activity_type="checkin",
            poi=narikala_poi,
            defaults={"xp_earned": 50}
        )
        FriendActivity.objects.get_or_create(
            user=nino,
            activity_type="level_up",
            defaults={"xp_earned": 200, "new_level": 5}
        )

        # PvP Challenge
        narikala_poi = created_pois[0]
        ChallengeInvite.objects.get_or_create(
            from_user=giorgi,
            to_user=demo_user,
            poi=narikala_poi,
            defaults={"status": "pending"}
        )

        # Also seed Eco Missions
        self.stdout.write("7. Seeding Eco Missions...")
        EcoMission.objects.get_or_create(
            mission_id="ECO-TURTLE-2026",
            defaults={
                "title": "Turtle Lake Eco Clean",
                "location_name": "Turtle Lake, Tbilisi",
                "task_description": "Clean up plastic waste around Turtle Lake",
                "reward_xp": 100,
                "reward_points": 50,
                "latitude": 41.7059,
                "longitude": 44.7546
            }
        )

        self.stdout.write(self.style.SUCCESS("Master Game Data Seeding Complete! You can now launch and play!"))
