import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelgo_core.settings')
django.setup()

from project_manager.models import Sprint, ProjectWiki, ProjectTask
from configuration.models import SystemConfig, OnboardingSlide, AppTranslation
from maps.models import PointOfInterest, RedZone
from partners.models import Category, Partner
from datetime import date

def seed_database():
    print("--- Seeding database with TravelGo bilingual specs...")

    # 1. System Config
    SystemConfig.objects.all().delete()
    SystemConfig.objects.create(
        checkin_radius_meters=40.0,
        referral_bonus_xp=100,
        referral_bonus_coins=50,
        app_maintenance_mode=False,
        min_app_version="1.0.0",
        app_name_ka="თრეველგო",
        app_name_en="TravelGo",
        maintenance_message_ka="მიმდინარეობს ტექნიკური სამუშაოები. გთხოვთ, შემოგვიერთდეთ მოგვიანებით.",
        maintenance_message_en="We are undergoing scheduled maintenance. Please check back later."
    )
    print("SystemConfig created.")

    # 2. Onboarding slides
    OnboardingSlide.objects.all().delete()
    OnboardingSlide.objects.create(
        title="მოგესალმებათ TravelGo",
        description="აღმოაჩინე საქართველოს ისტორიული და კულტურული საგანძური ინტერაქციულად.",
        title_en="Welcome to TravelGo",
        description_en="Discover Georgia's historical and cultural treasures interactively.",
        step_number=1,
        is_active=True
    )
    OnboardingSlide.objects.create(
        title="მიიღე რეალური ფასდაკლებები",
        description="დააგროვე ქულები ჩექ-ინების დროს და გადაცვალე პარტნიორი კაფეებისა და რესტორნების ფასდაკლებებში.",
        title_en="Earn Real Discounts",
        description_en="Collect points during check-ins and redeem them for partner discounts.",
        step_number=2,
        is_active=True
    )
    OnboardingSlide.objects.create(
        title="შექმენი შენი ავატარი",
        description="გახსენი უნიკალური რეგიონული სკინები და აჩვენე შენი პროგრესი მეგობრებს ლიდერბორდში.",
        title_en="Create Your Avatar",
        description_en="Unlock unique regional skins and show your progress on the leaderboard.",
        step_number=3,
        is_active=True
    )
    print("Onboarding slides created.")

    # 3. App Translations (Bilingual UI Keys)
    AppTranslation.objects.all().delete()
    
    # Auth
    translations = [
        ('auth_login_title', 'auth', 'შესვლა', 'Log In'),
        ('auth_signup_title', 'auth', 'რეგისტრაცია', 'Sign Up'),
        ('auth_email_label', 'auth', 'ელ.ფოსტა', 'Email Address'),
        ('auth_password_label', 'auth', 'პაროლი', 'Password'),
        ('auth_fullname_label', 'auth', 'სრული სახელი', 'Full Name'),
        ('auth_phone_label', 'auth', 'ტელეფონის ნომერი', 'Phone Number'),
        ('auth_forgot_pwd', 'auth', 'პაროლი დაგავიწყდათ?', 'Forgot Password?'),
        ('auth_login_btn', 'auth', 'შესვლა', 'Log In'),
        ('auth_signup_btn', 'auth', 'რეგისტრაცია', 'Sign Up'),
        ('auth_google_btn', 'auth', 'Google-ით შესვლა', 'Sign in with Google'),
        ('auth_apple_btn', 'auth', 'Apple-ით შესვლა', 'Sign in with Apple'),
        
        # Map & Details
        ('map_search_placeholder', 'map', 'მოძებნე ადგილი...', 'Search places...'),
        ('map_checkin_btn', 'map', 'ჩექ-ინი', 'Check-In'),
        ('map_audio_guide_btn', 'map', 'აუდიო გიდი', 'Audio Guide'),
        ('map_directions_btn', 'map', 'მარშრუტი', 'Get Directions'),
        ('map_hours_label', 'map', 'სამუშაო საათები', 'Open Hours'),
        ('map_rewards_label', 'map', 'ჯილდო', 'Rewards'),
        ('map_drops_label', 'map', 'ექსკლუზიური ნივთები', 'Exclusive Drops'),
        
        # Profile & Backpack
        ('profile_passport_title', 'profile', 'ციფრული პასპორტი', 'Digital Passport'),
        ('profile_visited_locations', 'profile', 'მონახულებული ადგილები', 'Visited Locations'),
        ('profile_backpack_title', 'profile', 'ზურგჩანთა', 'Backpack'),
        ('profile_skins_tab', 'profile', 'სკინები', 'Skins'),
        ('profile_badges_tab', 'profile', 'ბეჯები', 'Badges'),
        ('profile_logout_btn', 'profile', 'გასვლა', 'Log Out'),
        ('profile_referral_title', 'profile', 'მოიწვიე მეგობარი', 'Invite Friends'),
        ('profile_copy_code', 'profile', 'კოდის კოპირება', 'Copy Code'),
        ('profile_apply_code', 'profile', 'კოდის გამოყენება', 'Apply Code'),
        
        # Store & Partners
        ('store_discounts_title', 'store', 'პარტნიორი ფასდაკლებები', 'Partner Discounts'),
        ('store_my_coupons', 'store', 'ჩემი კუპონები', 'My Coupons'),
        ('store_redeem_btn', 'store', 'კუპონის გააქტიურება', 'Redeem Coupon'),
        ('store_use_coupon', 'store', 'ფასდაკლების გამოყენება', 'Use Coupon'),
        
        # AI Tour
        ('ai_planner_title', 'ai', 'AI ტურის დაგეგმვა', 'AI Tour Planner'),
        ('ai_interests_label', 'ai', 'რა გაინტერესებთ?', 'What are your interests?'),
        ('ai_hours_label', 'ai', 'რამდენი საათი გაქვთ?', 'How many hours do you have?'),
        ('ai_generate_btn', 'ai', 'მარშრუტის გენერაცია', 'Generate Itinerary'),
        
        # Errors & Validation
        ('err_invalid_email', 'errors', 'ელ.ფოსტის ფორმატი არასწორია', 'Invalid email format'),
        ('err_short_password', 'errors', 'პაროლი ძალიან მოკლეა (მინ. 8 სიმბოლო)', 'Password is too short (min 8 characters)'),
        ('err_password_match', 'errors', 'პაროლები არ ემთხვევა', 'Passwords do not match'),
        ('err_auth_failed', 'errors', 'ელ.ფოსტა ან პაროლი არასწორია', 'Invalid email or password'),
        ('err_too_far', 'errors', 'ძალიან შორს ხართ! ჩექ-ინისთვის მიუახლოვდით ლოკაციას.', 'You are too far! Please get closer to check in.'),
        ('err_no_camera', 'errors', 'კამერაზე წვდომა აუცილებელია AR რეჟიმისთვის', 'Camera permission is required for AR mode'),
    ]

    for key, cat, ka, en in translations:
        AppTranslation.objects.create(key=key, category=cat, text_ka=ka, text_en=en)
    print("App UI Translations created.")

    # 4. Project Wiki
    ProjectWiki.objects.all().delete()
    ProjectWiki.objects.create(
        title="Design Principles",
        category='branding',
        content="""# Design Principles

1. **Clarity:** Interfaces should be intuitive with minimal text and clear icons.
2. **Engagement:** Use vibrant visuals, animations, and AR overlays.
3. **Local Flavor:** Incorporate Georgian cultural motifs and colors.
4. **Consistency:** Maintain a cohesive visual language.
5. **Accessibility:** Ensure readability and appropriate tap sizes."""
    )
    ProjectWiki.objects.create(
        title="Branding Vision & Style Guide",
        category='branding',
        content="""# Branding Vision & Style Guide

### Color Palette:
* **Primary:** Deep Emerald (`#006749`)
* **Secondary:** Warm Amber (`#FFB400`)
* **UI Shell / Text:** Slate Gray (`#2E3A46`)
* **Background:** Ivory White (`#F9F7F1`)"""
    )
    print("Project Wiki documents created.")

    # 5. Sprints
    Sprint.objects.all().delete()
    s1 = Sprint.objects.create(
        title="Phase 1: API Connections",
        description="Sync check-in and quest APIs between mobile and backend.",
        start_date=date(2025, 4, 1),
        end_date=date(2025, 4, 15),
        is_completed=True
    )
    s2 = Sprint.objects.create(
        title="Phase 2: Screen Dynamization",
        description="Replace static mock profiles and leaderboard screens with API data.",
        start_date=date(2025, 4, 16),
        end_date=date(2025, 4, 30),
        is_completed=True
    )
    s3 = Sprint.objects.create(
        title="Phase 3: Backend Optimization (Production Ready)",
        description="Secrets clean up, migrate to PostgreSQL/PostGIS, Cloudinary media storage.",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 15),
        is_completed=False
    )
    s4 = Sprint.objects.create(
        title="Phase 4-5: SDK & Grant Demo Mode",
        description="Convert features to SDK and implement isDemoMode mock GPS for GITA jury.",
        start_date=date(2025, 5, 16),
        end_date=date(2025, 5, 30),
        is_completed=False
    )
    print("Sprints created.")

    # 6. Core tasks
    ProjectTask.objects.all().delete()
    ProjectTask.objects.create(
        title="Sync Check-in Endpoint (Task 1.1)",
        description="Update map_repository.dart to request /maps/checkin/ instead of /quests/check-in/.",
        priority='critical',
        status='done',
        sprint=s1
    )
    ProjectTask.objects.create(
        title="Dynamize Leaderboard Screen (Task 2.2)",
        description="Fetch real users sorted by XP using LeaderboardProvider.fetchLeaderboard().",
        priority='high',
        status='done',
        sprint=s2
    )
    ProjectTask.objects.create(
        title="Database Migration (Task 3.2)",
        description="Migrate SQLite database to PostgreSQL with PostGIS extension.",
        priority='critical',
        status='todo',
        sprint=s3
    )
    ProjectTask.objects.create(
        title="Mock GPS Demo Mode (Task 5.1)",
        description="Implement isDemoMode in map_provider.dart to allow remote check-ins for the jury.",
        priority='high',
        status='todo',
        sprint=s4
    )
    print("Project Tasks created.")

    # 7. Update POIs with Bilingual values
    PointOfInterest.objects.all().delete()
    PointOfInterest.objects.create(
        name="თბილისის სატელევიზიო ანძა",
        name_en="Tbilisi TV Tower",
        description="თბილისის სატელევიზიო ანძა — სამაუწყებლო ანძა თბილისში, მთაწმინდის პარკში.",
        description_en="The Tbilisi TV Tower is a free-standing tower structure used for communications purposes in Mtatsminda Park.",
        open_hours="24/7",
        open_hours_en="24/7",
        poi_type="historical",
        latitude=41.6961,
        longitude=44.7871,
        base_xp=100,
        reward_badge_name="Mtatsminda Explorer"
    )
    PointOfInterest.objects.create(
        name="სვეტიცხოვლის საკათედრო ტაძარი",
        name_en="Svetitskhoveli Cathedral",
        description="სვეტიცხოვლის საკათედრო ტაძარი — საქართველოს მართლმადიდებელი ეკლესიის საპატრიარქო ტაძარი მცხეთაში.",
        description_en="Svetitskhoveli Cathedral is an Eastern Orthodox cathedral located in the historic town of Mtskheta.",
        open_hours="09:00 - 19:00",
        open_hours_en="09:00 AM - 07:00 PM",
        poi_type="historical",
        latitude=41.8422,
        longitude=44.7211,
        base_xp=150,
        reward_badge_name="Mtskheta Pilgrim"
    )
    print("Bilingual POIs created.")

    # 8. Update Categories and Partners
    Category.objects.all().delete()
    cat_food = Category.objects.create(name="კაფეები & რესტორნები", name_en="Cafes & Restaurants", icon_name="restaurant")
    cat_hotel = Category.objects.create(name="სასტუმროები", name_en="Hotels & Stays", icon_name="hotel")

    Partner.objects.all().delete()
    Partner.objects.create(
        name="შოკოლადის სახლი",
        name_en="Chocolate House",
        category=cat_food,
        location_address="მთაწმინდის ქ. 12",
        location_address_en="12 Mtatsminda St",
        latitude=41.6965,
        longitude=44.7875,
        offer_percentage=10,
        description="მიიღეთ 10%-იანი ფასდაკლება ყველა სახის შოკოლადზე და ტკბილეულზე.",
        description_en="Get 10% discount on all chocolates and sweets.",
        terms_and_conditions="ფასდაკლება ვრცელდება მხოლოდ ადგილზე შეკვეთისას.",
        terms_and_conditions_en="The discount is valid for dine-in orders only."
    )
    print("Bilingual Categories and Partners created.")
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    seed_database()
