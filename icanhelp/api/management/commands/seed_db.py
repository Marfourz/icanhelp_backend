import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from api.models import Category, UserProfil

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with categories and admin user"

    def handle(self, *args, **options):

        # 1️⃣ Site domain (supprime "example.com" dans les emails)
        site_domain = os.getenv('SITE_DOMAIN', 'localhost:8000')
        Site.objects.update_or_create(
            id=1,
            defaults={'domain': site_domain, 'name': 'Skillou'},
        )

        self.stdout.write("✅ Categories ready")

        # 2️⃣ Admin user (env)
        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not all([username, password]):
            self.stdout.write("⚠️ Admin env vars missing, skipping admin creation")
            return

        admin, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            admin.set_password(password)
            admin.save()
            self.stdout.write("👑 Admin user created")
        else:
            self.stdout.write("👑 Admin user already exists")

        # 3️⃣ Admin profile
        UserProfil.objects.get_or_create(
            user=admin,
            defaults={
                "bio": "Administrateur de la plateforme",
                "city": "Rennes",
                "points": 1000,
            },
        )

        self.stdout.write(self.style.SUCCESS("🚀 Database seeded successfully"))
