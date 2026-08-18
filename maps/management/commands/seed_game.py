import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser
from maps.models import PointOfInterest, RedZone, CheckIn
from inventory.models import Badge, Skin, UserInventory
from quests.models import QuizQuestion, DailyQuest, UserQuizSubmission, UserPuzzleSubmission, UserQuestProgress
from partners.models import Partner, Category, DiscountCoupon
from eco_missions.models import EcoMission, Landmark, UserMissionProgress, WasteType
from social.models import Friendship, FriendActivity, ChallengeInvite
from configuration.models import SystemConfig, OnboardingSlide, AppTranslation, ARTutorialStep

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed TravelGo database with 5+ rich test records across EVERY Django Admin model'

    def handle(self, *args, **options):
        self.stdout.write("Starting Exhaustive TravelGo Data Seeding (5+ in ALL Admin Models)...")

        # 1. SEED SYSTEM CONFIG & APP CONFIGURATION
        self.stdout.write("1. Seeding System Config & App Configuration...")
        SystemConfig.objects.get_or_create(
            pk=1,
            defaults={
                "checkin_radius_meters": 40.0,
                "referral_bonus_xp": 100,
                "referral_bonus_coins": 50,
                "app_name_ka": "თრეველგო",
                "app_name_en": "TravelGo",
            }
        )

        # Onboarding Slides (5)
        onboarding_data = [
            {"step_number": 1, "title": "აღმოაჩინე საქართველო", "description": "იმოგზაურე ისტორიულ და თანამედროვე ლოკაციებზე", "title_en": "Discover Georgia", "description_en": "Explore historical and modern locations"},
            {"step_number": 2, "title": "შეაგროვე ქულები", "description": "გაიარე ჩექინები, ამოხსენი ქვიზები და მოიგე კოინები", "title_en": "Earn Rewards", "description_en": "Check in, solve quizzes, and earn coins"},
            {"step_number": 3, "title": "გამოიყენე AR რეჟიმი", "description": "იპოვე დამალული ჯილდოები კამერის საშუალებით", "title_en": "Use AR Mode", "description_en": "Find hidden rewards using your camera"},
            {"step_number": 4, "title": "მიიღე ფასდაკლებები", "description": "გაცვალე მონეტები პარტნიორების ფასდაკლების კუპონებში", "title_en": "Get Discounts", "description_en": "Redeem coins for partner discount coupons"},
            {"step_number": 5, "title": "გამოიწვიე მეგობრები", "description": "შეეჯიბრე მეგობრებს და გახდი ლიდერბორდის ჩემპიონი", "title_en": "Challenge Friends", "description_en": "Compete with friends and lead the leaderboard"},
        ]
        for ob in onboarding_data:
            OnboardingSlide.objects.get_or_create(step_number=ob["step_number"], defaults=ob)

        # App Translations (5)
        translations_data = [
            {"key": "welcome_btn", "category": "auth", "text_ka": "დაწყება", "text_en": "Get Started"},
            {"key": "map_checkin_btn", "category": "map", "text_ka": "ჩექინის გაკეთება", "text_en": "Check In"},
            {"key": "profile_coins_label", "category": "profile", "text_ka": "ჩემი მონეტები", "text_en": "My Coins"},
            {"key": "store_coupon_redeem", "category": "store", "text_ka": "კუპონის მიღება", "text_en": "Redeem Coupon"},
            {"key": "ai_planner_title", "category": "ai", "text_ka": "AI ტურის დაგეგმვა", "text_en": "AI Tour Planner"},
        ]
        for tr in translations_data:
            AppTranslation.objects.get_or_create(key=tr["key"], defaults=tr)

        # AR Tutorial Steps (5)
        ar_steps = [
            {"step_number": 1, "target_action": "look_around", "instruction_ka": "დაატრიალეთ ტელეფონი კამერით ლოკაციის დასანახად", "instruction_en": "Rotate your phone to locate the POI"},
            {"step_number": 2, "target_action": "tap_poi", "instruction_ka": "დააჭირეთ ეკრანზე გამოჩენილ 3D ობიექტს", "instruction_en": "Tap the 3D object displayed on screen"},
            {"step_number": 3, "target_action": "checkin", "instruction_ka": "დააჭირეთ ჩექინის ღილაკს ჯილდოს მისაღებად", "instruction_en": "Tap Check-in button to claim reward"},
            {"step_number": 4, "target_action": "look_around", "instruction_ka": "მოძებნეთ AR მონეტები ჰაერში", "instruction_en": "Find AR coins in the air"},
            {"step_number": 5, "target_action": "checkin", "instruction_ka": "გილოცავთ! თქვენ მიიღეთ 50 მონეტა", "instruction_en": "Congratulations! You earned 50 coins"},
        ]
        for ar in ar_steps:
            ARTutorialStep.objects.get_or_create(step_number=ar["step_number"], defaults=ar)

        # 2. SEED SHOP ITEMS (5 Badges & 5 Skins)
        self.stdout.write("2. Seeding Shop Items (5 Badges & 5 Skins)...")
        badges_list = []
        badges_data = [
            {"name": "Eco Guardian Badge", "description": "Awarded for eco cleanup missions", "coin_price": 50, "is_for_sale": True, "rarity": "rare"},
            {"name": "Explorer Supreme", "description": "Visited over 10 historic locations", "coin_price": 100, "is_for_sale": True, "rarity": "epic"},
            {"name": "Narikala Conqueror", "description": "Checked in at Narikala Fortress", "coin_price": 75, "is_for_sale": True, "rarity": "common"},
            {"name": "Master Navigator", "description": "Completed 5 PvP Challenges", "coin_price": 150, "is_for_sale": True, "rarity": "legendary"},
            {"name": "Wine Connoisseur", "description": "Visited 3 top Georgian wineries", "coin_price": 120, "is_for_sale": True, "rarity": "rare"},
        ]
        for bdata in badges_data:
            b, _ = Badge.objects.get_or_create(name=bdata["name"], defaults=bdata)
            badges_list.append(b)

        skins_list = []
        skins_data = [
            {"name": "Georgian Chokha Special", "description": "Traditional royal Georgian national dress", "coin_price": 200, "is_for_sale": True},
            {"name": "Golden Knight Armor", "description": "Epic golden medieval armor", "coin_price": 350, "is_for_sale": True},
            {"name": "Cyberpunk Explorer", "description": "Futuristic cyberpunk travel jacket", "coin_price": 250, "is_for_sale": True},
            {"name": "Royal Crown", "description": "Golden King Vakhtang Gorgasali crown", "coin_price": 180, "is_for_sale": True},
            {"name": "Svaneti Mountain Coat", "description": "Warm authentic mountain wool coat", "coin_price": 220, "is_for_sale": True},
        ]
        for sdata in skins_data:
            s, _ = Skin.objects.get_or_create(name=sdata["name"], defaults=sdata)
            skins_list.append(s)

        # 3. SEED TEST USERS (5 Users)
        self.stdout.write("3. Seeding Test Users (5 Competitors)...")
        test_users_data = [
            {"email": "giorgi@travelgo.ge", "username": "giorgi_traveler", "full_name": "Giorgi Beridze", "xp": 1450, "level": 4, "coins": 350},
            {"email": "nino@travelgo.ge", "username": "nino_adventurer", "full_name": "Nino Kapanadze", "xp": 2100, "level": 5, "coins": 500},
            {"email": "luka@travelgo.ge", "username": "luka_explorer", "full_name": "Luka Gelashvili", "xp": 980, "level": 3, "coins": 200},
            {"email": "ana@travelgo.ge", "username": "ana_georgia", "full_name": "Ana Maisuradze", "xp": 3200, "level": 7, "coins": 850},
            {"email": "davit@travelgo.ge", "username": "davit_king", "full_name": "Davit Shervashidze", "xp": 4100, "level": 9, "coins": 1200},
        ]
        created_users = []
        for udata in test_users_data:
            u, _ = User.objects.get_or_create(email=udata["email"], defaults=udata)
            created_users.append(u)

        demo_user, _ = User.objects.get_or_create(
            email="testuser@travelgo.ge",
            defaults={"username": "demo_traveler", "full_name": "Demo Traveler", "xp": 1200, "level": 3, "coins": 450}
        )

        # Seed User Inventories (5)
        for i, user in enumerate(created_users):
            UserInventory.objects.get_or_create(user=user, badge=badges_list[i % len(badges_list)])
            UserInventory.objects.get_or_create(user=user, skin=skins_list[i % len(skins_list)])

        # 4. SEED POIS & RED ZONES (13 POIs, 5 Red Zones, 5 Check-ins)
        self.stdout.write("4. Seeding POIs, Red Zones & Check-ins...")
        pois_data = [
            {"name": "Narikala Fortress", "description": "IV saukunis istoriuli tsikhesimagre", "latitude": 41.6875, "longitude": 44.8082, "base_xp": 50, "poi_type": "historical"},
            {"name": "Holy Trinity Cathedral (Sameba)", "description": "Sakartvelos mtavari sakatedro tadzari", "latitude": 41.6976, "longitude": 44.8059, "base_xp": 40, "poi_type": "historical"},
            {"name": "The Bridge of Peace", "description": "Tanamedrove sapegmavlo khidi", "latitude": 41.6935, "longitude": 44.8088, "base_xp": 30, "poi_type": "tourist"},
            {"name": "Mtatsminda Park", "description": "Panoramuli parki mtatsmindis platoze", "latitude": 41.6932, "longitude": 44.7851, "base_xp": 45, "poi_type": "park"},
            {"name": "Old Tbilisi Sulfur Baths", "description": "Abanotubani - gogirdis abanoebi", "latitude": 41.6885, "longitude": 44.8108, "base_xp": 35, "poi_type": "historical"},
        ]
        created_pois = []
        for pdata in pois_data:
            poi, _ = PointOfInterest.objects.get_or_create(name=pdata["name"], defaults=pdata)
            created_pois.append(poi)

        red_zones_data = [
            {"name": "Narikala Steep Cliff", "name_en": "Narikala Steep Cliff", "center_latitude": 41.6872, "center_longitude": 44.8080, "radius_meters": 35, "warning_message": "Caution: Steep cliff zone near Narikala"},
            {"name": "Mtkvari Rapid River Shore", "name_en": "Mtkvari Rapid River Shore", "center_latitude": 41.6938, "center_longitude": 44.8092, "radius_meters": 25, "warning_message": "Warning: Fast river current zone"},
            {"name": "Mtatsminda Funicular Track", "name_en": "Mtatsminda Funicular Track", "center_latitude": 41.6930, "center_longitude": 44.7860, "radius_meters": 30, "warning_message": "Do not step on train tracks"},
            {"name": "Turtle Lake Deep Shore", "name_en": "Turtle Lake Deep Shore", "center_latitude": 41.7061, "center_longitude": 44.7550, "radius_meters": 20, "warning_message": "Deep water zone"},
            {"name": "Jvari Cliff Edge", "name_en": "Jvari Cliff Edge", "center_latitude": 41.8385, "center_longitude": 44.7335, "radius_meters": 40, "warning_message": "High cliff edge hazard"},
        ]
        for rz in red_zones_data:
            RedZone.objects.get_or_create(name=rz["name"], defaults=rz)

        # Seed 5 CheckIns
        for i, user in enumerate(created_users):
            CheckIn.objects.get_or_create(
                user=user,
                poi=created_pois[i % len(created_pois)],
                defaults={"xp_earned": 50, "user_lat": created_pois[i % len(created_pois)].latitude, "user_lon": created_pois[i % len(created_pois)].longitude}
            )

        # 5. SEED PARTNERS & COUPONS (5 Categories, 5 Partners, 5 Coupons)
        self.stdout.write("5. Seeding Partners & Discount Coupons...")
        cat_rest, _ = Category.objects.get_or_create(name="Restaurant", defaults={"icon_name": "utensils"})
        cat_wine, _ = Category.objects.get_or_create(name="Winery", defaults={"icon_name": "wine-glass"})
        cat_hotel, _ = Category.objects.get_or_create(name="Hotel & Cafe", defaults={"icon_name": "hotel"})
        cat_cafe, _ = Category.objects.get_or_create(name="Bakery & Cafe", defaults={"icon_name": "coffee"})
        cat_activity, _ = Category.objects.get_or_create(name="Adventure & Tour", defaults={"icon_name": "compass"})

        partners_data = [
            {"name": "Chateau Mukhrani Winery", "category": cat_wine, "latitude": 41.9408, "longitude": 44.5786, "offer_percentage": 20, "description": "Royal estate and wine degustation in Kartli.", "location_address": "Mukhrani, Kartli"},
            {"name": "Barbarestan Restaurant", "category": cat_rest, "latitude": 41.7100, "longitude": 44.7950, "offer_percentage": 15, "description": "Authentic Georgian cuisine based on 19th-century recipes.", "location_address": "D. Aghmashenebeli Ave 132, Tbilisi"},
            {"name": "Fabrika Tbilisi", "category": cat_hotel, "latitude": 41.7065, "longitude": 44.7929, "offer_percentage": 10, "description": "Urban hotspot, hostel, and open-air cafes.", "location_address": "E. Ninoshvili St 8, Tbilisi"},
            {"name": "Puri Guliani Bakery", "category": cat_cafe, "latitude": 41.6945, "longitude": 44.8070, "offer_percentage": 12, "description": "Traditional Georgian artisan bread and breakfast.", "location_address": "Saarbeucken Sq, Tbilisi"},
            {"name": "Svaneti Zipline Extreme", "category": cat_activity, "latitude": 43.0450, "longitude": 42.7300, "offer_percentage": 25, "description": "Thrilling mountain zipline adventure over Mestia.", "location_address": "Mestia Center, Svaneti"},
        ]
        for part_data in partners_data:
            partner, created = Partner.objects.get_or_create(name=part_data["name"], defaults=part_data)
            if not created:
                partner.offer_percentage = part_data["offer_percentage"]
                partner.save()
            DiscountCoupon.objects.get_or_create(
                partner=partner,
                defaults={
                    "discount_pct": partner.offer_percentage,
                    "status": "active",
                    "valid_until": "2026-12-31"
                }
            )

        # 6. SEED QUESTS & QUIZZES & SUBMISSIONS (5 Quests, 5 Quiz Questions, 5 Progresses)
        self.stdout.write("6. Seeding Quests, Quizzes & Submissions...")
        for poi in created_pois:
            DailyQuest.objects.get_or_create(
                poi=poi,
                defaults={"title": f"Visit {poi.name}", "description": f"Visit {poi.name} and check in to claim rewards", "reward_xp": 50, "reward_coins": 25, "date_active": date.today()}
            )
            QuizQuestion.objects.get_or_create(
                poi=poi,
                question=f"რომელ საუკუნეში აშენდა {poi.name}?",
                defaults={"option_a": "IV საუკუნე", "option_b": "VI საუკუნე", "option_c": "XI საუკუნე", "option_d": "XIX საუკუნე", "correct_index": 0}
            )

        quests = list(DailyQuest.objects.all()[:5])
        for i, user in enumerate(created_users):
            if i < len(quests):
                UserQuestProgress.objects.get_or_create(user=user, quest=quests[i], defaults={"progress": 1, "is_completed": True})
                UserQuizSubmission.objects.get_or_create(user=user, poi=quests[i].poi, defaults={"score": 5})
                UserPuzzleSubmission.objects.get_or_create(user=user, poi=quests[i].poi, defaults={"completion_time_seconds": 45, "moves_count": 12})

        # 7. SEED ECO MISSIONS & LANDMARKS & PROGRESS (5 Missions, 5 Landmarks, 5 Progresses)
        self.stdout.write("7. Seeding Eco Missions, Landmarks & User Progress...")
        eco_missions_data = [
            {"mission_id": "ECO-TURTLE-2026", "title": "Turtle Lake Eco Clean", "location_name": "Turtle Lake, Tbilisi", "task_description": "Clean up plastic waste around Turtle Lake", "reward_xp": 100, "reward_points": 50, "latitude": 41.7059, "longitude": 44.7546},
            {"mission_id": "ECO-LISSI-2026", "title": "Lisi Lake Green Park", "location_name": "Lisi Lake, Tbilisi", "task_description": "Collect paper and bottle caps along Lisi path", "reward_xp": 80, "reward_points": 40, "latitude": 41.7450, "longitude": 44.7370},
            {"mission_id": "ECO-MTSKETA-2026", "title": "Mtkvari River Shore Care", "location_name": "Mtskheta Confluence", "task_description": "Clean riverbank area near Aragvi-Mtkvari join", "reward_xp": 120, "reward_points": 60, "latitude": 41.8400, "longitude": 44.7250},
            {"mission_id": "ECO-BATUMI-2026", "title": "Batumi Boulevard Beach Clean", "location_name": "Batumi Coast", "task_description": "Remove plastic bottles from black sea pebble beach", "reward_xp": 150, "reward_points": 75, "latitude": 41.6510, "longitude": 41.6340},
            {"mission_id": "ECO-MESTIA-2026", "title": "Svaneti Alpine Trail Care", "location_name": "Mestia Hike Path", "task_description": "Keep alpine hiking trails trash free", "reward_xp": 200, "reward_points": 100, "latitude": 43.0460, "longitude": 42.7310},
        ]
        created_eco_missions = []
        for eco in eco_missions_data:
            m, _ = EcoMission.objects.get_or_create(mission_id=eco["mission_id"], defaults=eco)
            created_eco_missions.append(m)

        for i, user in enumerate(created_users):
            UserMissionProgress.objects.get_or_create(user=user, mission=created_eco_missions[i % len(created_eco_missions)], defaults={"status": "completed"})

        landmarks_data = [
            {"name_ka": "ნარიყალას ციხე-სიმაგრე", "name_en": "Narikala Fortress", "category": "historical", "address": "ძველი თბილისი", "latitude": 41.6875, "longitude": 44.8082},
            {"name_ka": "სამების საკათედრო ტაძარი", "name_en": "Holy Trinity Cathedral", "category": "historical", "address": "ელიას მთა, თბილისი", "latitude": 41.6976, "longitude": 44.8059},
            {"name_ka": "მშვიდობის ხიდი", "name_en": "Bridge of Peace", "category": "modern", "address": "რიყის პარკი, თბილისი", "latitude": 41.6935, "longitude": 44.8088},
            {"name_ka": "სვეტიცხოვლის ტაძარი", "name_en": "Svetitskhoveli Cathedral", "category": "historical", "address": "მცხეთა", "latitude": 41.8422, "longitude": 44.7208},
            {"name_ka": "ბათუმის ბულვარი", "name_en": "Batumi Boulevard", "category": "modern", "address": "ბათუმი", "latitude": 41.6500, "longitude": 41.6333},
        ]
        for lm in landmarks_data:
            Landmark.objects.get_or_create(name_ka=lm["name_ka"], defaults=lm)

        # 8. SEED SOCIAL FRIENDSHIPS, ACTIVITIES & PVP CHALLENGES (5 Each)
        self.stdout.write("8. Seeding Social Friendships, Feed & 5 PvP Challenges...")
        giorgi = created_users[0]
        nino = created_users[1]
        luka = created_users[2]
        ana = created_users[3]
        davit = created_users[4]

        # 5 Friendships
        Friendship.objects.get_or_create(from_user=demo_user, to_user=giorgi, defaults={"status": "accepted"})
        Friendship.objects.get_or_create(from_user=demo_user, to_user=nino, defaults={"status": "accepted"})
        Friendship.objects.get_or_create(from_user=demo_user, to_user=luka, defaults={"status": "accepted"})
        Friendship.objects.get_or_create(from_user=demo_user, to_user=ana, defaults={"status": "accepted"})
        Friendship.objects.get_or_create(from_user=demo_user, to_user=davit, defaults={"status": "accepted"})

        # 5 Social Feed Activities
        narikala_poi = created_pois[0]
        FriendActivity.objects.get_or_create(user=giorgi, activity_type="checkin", poi=narikala_poi, defaults={"xp_earned": 50})
        FriendActivity.objects.get_or_create(user=nino, activity_type="level_up", defaults={"xp_earned": 200, "new_level": 5})
        FriendActivity.objects.get_or_create(user=luka, activity_type="quest_complete", defaults={"xp_earned": 100})
        FriendActivity.objects.get_or_create(user=ana, activity_type="badge_unlock", defaults={"xp_earned": 150})
        FriendActivity.objects.get_or_create(user=davit, activity_type="checkin", poi=narikala_poi, defaults={"xp_earned": 70})

        # 5 PvP Challenge Invites
        ChallengeInvite.objects.get_or_create(from_user=giorgi, to_user=demo_user, poi=narikala_poi, defaults={"message": "Let's hike Narikala!", "status": "pending"})
        ChallengeInvite.objects.get_or_create(from_user=nino, to_user=demo_user, poi=narikala_poi, defaults={"message": "Race to Mtatsminda!", "status": "pending"})
        ChallengeInvite.objects.get_or_create(from_user=luka, to_user=demo_user, poi=narikala_poi, defaults={"message": "Bridge of Peace photo challenge", "status": "pending"})
        ChallengeInvite.objects.get_or_create(from_user=ana, to_user=demo_user, poi=narikala_poi, defaults={"message": "Mtskheta weekend trip", "status": "pending"})
        ChallengeInvite.objects.get_or_create(from_user=davit, to_user=demo_user, poi=narikala_poi, defaults={"message": "Svaneti Alpine challenge", "status": "pending"})

        self.stdout.write(self.style.SUCCESS("Exhaustive Master Game Data Seeding Complete! EVERY admin model has 5+ records."))
