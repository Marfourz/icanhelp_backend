import requests
from django.core.management.base import BaseCommand
from django.conf import settings
import os

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "REMPLACE_PAR_TA_CLE_UNSPLASH")
UNSPLASH_URL = "https://api.unsplash.com/photos/random"

# URL de ton API Django
API_BASE_URL = 'http://localhost:8000'
API_LOGIN_URL = f"{API_BASE_URL}/api/token"
API_CATEGORIES_URL = f"{API_BASE_URL}/category/"

CATEGORIES = [
    # ── Racines ──────────────────────────────────────────────────────────
    {"name": "Tech & Informatique",  "parent": None, "icon_name": "computer",         "color": "#4A90E2", "query": "technology computer"},
    {"name": "Sport & Fitness",      "parent": None, "icon_name": "fitness_center",   "color": "#E25B4A", "query": "sport fitness"},
    {"name": "Musique & Arts",       "parent": None, "icon_name": "music_note",       "color": "#9B59B6", "query": "music arts"},
    {"name": "Langues",              "parent": None, "icon_name": "language",         "color": "#2ECC71", "query": "language books study"},
    {"name": "Cuisine",              "parent": None, "icon_name": "restaurant",       "color": "#E67E22", "query": "cooking food kitchen"},
    {"name": "Business & Finance",   "parent": None, "icon_name": "business_center",  "color": "#1ABC9C", "query": "business finance office"},

    # ── Tech ─────────────────────────────────────────────────────────────
    {"name": "Développement Web",    "parent": "Tech & Informatique", "icon_name": "web",              "color": "#5BA3F5", "query": "web development code"},
    {"name": "Développement Mobile", "parent": "Tech & Informatique", "icon_name": "smartphone",       "color": "#5BA3F5", "query": "mobile app smartphone"},
    {"name": "Data Science & IA",    "parent": "Tech & Informatique", "icon_name": "analytics",        "color": "#5BA3F5", "query": "data science artificial intelligence"},
    {"name": "Cybersécurité",        "parent": "Tech & Informatique", "icon_name": "security",         "color": "#5BA3F5", "query": "cybersecurity"},
    {"name": "DevOps & Cloud",       "parent": "Tech & Informatique", "icon_name": "cloud",            "color": "#5BA3F5", "query": "cloud computing server"},
    {"name": "UI/UX Design",         "parent": "Tech & Informatique", "icon_name": "design_services",  "color": "#5BA3F5", "query": "ux design interface"},

    # ── Sport ────────────────────────────────────────────────────────────
    {"name": "Football",             "parent": "Sport & Fitness", "icon_name": "sports_soccer",        "color": "#E87060", "query": "football soccer"},
    {"name": "Basketball",           "parent": "Sport & Fitness", "icon_name": "sports_basketball",    "color": "#E87060", "query": "basketball"},
    {"name": "Tennis",               "parent": "Sport & Fitness", "icon_name": "sports_tennis",        "color": "#E87060", "query": "tennis"},
    {"name": "Natation",             "parent": "Sport & Fitness", "icon_name": "pool",                 "color": "#E87060", "query": "swimming pool"},
    {"name": "Yoga & Méditation",    "parent": "Sport & Fitness", "icon_name": "self_improvement",     "color": "#E87060", "query": "yoga meditation"},
    {"name": "Arts Martiaux",        "parent": "Sport & Fitness", "icon_name": "sports_martial_arts",  "color": "#E87060", "query": "martial arts karate"},

    # ── Musique & Arts ───────────────────────────────────────────────────
    {"name": "Guitare",              "parent": "Musique & Arts", "icon_name": "music_note",  "color": "#AF6FCC", "query": "guitar music"},
    {"name": "Piano",                "parent": "Musique & Arts", "icon_name": "piano",       "color": "#AF6FCC", "query": "piano keys"},
    {"name": "Chant",                "parent": "Musique & Arts", "icon_name": "mic",         "color": "#AF6FCC", "query": "singing microphone"},
    {"name": "Dessin & Peinture",    "parent": "Musique & Arts", "icon_name": "brush",       "color": "#AF6FCC", "query": "painting drawing art"},
    {"name": "Photographie",         "parent": "Musique & Arts", "icon_name": "camera_alt",  "color": "#AF6FCC", "query": "photography camera"},
    {"name": "Danse",                "parent": "Musique & Arts", "icon_name": "nightlife",   "color": "#AF6FCC", "query": "dance"},

    # ── Langues ──────────────────────────────────────────────────────────
    {"name": "Anglais",   "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "english language london"},
    {"name": "Espagnol",  "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "spanish language spain"},
    {"name": "Arabe",     "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "arabic language"},
    {"name": "Japonais",  "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "japanese language tokyo"},
    {"name": "Mandarin",  "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "chinese language beijing"},
    {"name": "Allemand",  "parent": "Langues", "icon_name": "language", "color": "#45D98A", "query": "german language berlin"},

    # ── Cuisine ──────────────────────────────────────────────────────────
    {"name": "Cuisine Française",    "parent": "Cuisine", "icon_name": "restaurant",    "color": "#F0922E", "query": "french cuisine food"},
    {"name": "Cuisine Africaine",    "parent": "Cuisine", "icon_name": "ramen_dining",  "color": "#F0922E", "query": "african food"},
    {"name": "Pâtisserie",           "parent": "Cuisine", "icon_name": "cake",          "color": "#F0922E", "query": "pastry cake dessert"},
    {"name": "Cuisine Végétarienne", "parent": "Cuisine", "icon_name": "eco",           "color": "#F0922E", "query": "vegetarian food vegetables"},
    {"name": "Barbecue & Grillades", "parent": "Cuisine", "icon_name": "outdoor_grill", "color": "#F0922E", "query": "barbecue grill"},
    {"name": "Boulangerie",          "parent": "Cuisine", "icon_name": "bakery_dining", "color": "#F0922E", "query": "bakery bread"},

    # ── Business ─────────────────────────────────────────────────────────
    {"name": "Comptabilité",          "parent": "Business & Finance", "icon_name": "calculate",      "color": "#26D4B4", "query": "accounting finance"},
    {"name": "Marketing Digital",     "parent": "Business & Finance", "icon_name": "campaign",       "color": "#26D4B4", "query": "digital marketing"},
    {"name": "Gestion de Projet",     "parent": "Business & Finance", "icon_name": "assignment",     "color": "#26D4B4", "query": "project management team"},
    {"name": "Investissement & Bourse","parent": "Business & Finance","icon_name": "show_chart",     "color": "#26D4B4", "query": "stock market investment"},
    {"name": "Entrepreneuriat",       "parent": "Business & Finance", "icon_name": "rocket_launch",  "color": "#26D4B4", "query": "entrepreneur startup"},
    {"name": "Ressources Humaines",   "parent": "Business & Finance", "icon_name": "people",         "color": "#26D4B4", "query": "human resources team"},
]


class Command(BaseCommand):
    help = "Crée les catégories via l'API avec leurs images Unsplash"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username admin')
        parser.add_argument('--password', type=str, required=True, help='Password admin')
        parser.add_argument('--force',    action='store_true',     help='Recréer si déjà existant')

    def handle(self, *args, **options):
        # 1. Login pour obtenir le token
        token = self.get_token(options['username'], options['password'])
        if not token:
            self.stdout.write(self.style.ERROR("❌ Authentification échouée."))
            return

        headers = {"Authorization": f"Bearer {token}"}
        created_categories = {}  # name → id
        success, skipped, failed = 0, 0, 0

        for cat in CATEGORIES:
            # Résoudre le parent_id
            parent_id = None
            if cat["parent"]:
                parent_id = created_categories.get(cat["parent"])
                if not parent_id:
                    self.stdout.write(self.style.ERROR(
                        f"❌ {cat['name']} — parent '{cat['parent']}' introuvable"
                    ))
                    failed += 1
                    continue

            # Télécharger l'image depuis Unsplash
            image_content, filename = self.fetch_image(cat["name"], cat["query"])
            if not image_content:
                failed += 1
                continue

            # Appel API pour créer la catégorie
            try:
                files = {"image": (filename, image_content, "image/jpeg")}
                data = {
                    "name":      cat["name"],
                    "icon_name": cat["icon_name"],
                    "color":     cat["color"],
                }
                if parent_id:
                    data["parent"] = parent_id

                response = requests.post(
                    API_CATEGORIES_URL,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=15
                )

                if response.status_code == 201:
                    category_id = response.json().get("id")
                    created_categories[cat["name"]] = category_id
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ {cat['name']} (id={category_id})"
                    ))
                    success += 1

                elif response.status_code == 400 and not options['force']:
                    self.stdout.write(f"⏭  {cat['name']} — déjà existant")
                    # Récupérer l'id existant pour les sous-catégories
                    existing = self.get_existing_id(cat["name"], headers)
                    if existing:
                        created_categories[cat["name"]] = existing
                    skipped += 1

                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ {cat['name']} — {response.status_code} : {response.text}"
                    ))
                    failed += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {cat['name']} — {e}"))
                failed += 1

        self.stdout.write("\n─────────────────────────────")
        self.stdout.write(self.style.SUCCESS(f"✅  Créés   : {success}"))
        self.stdout.write(self.style.WARNING(f"⏭  Ignorés : {skipped}"))
        self.stdout.write(self.style.ERROR  (f"❌  Échecs  : {failed}"))

    def get_token(self, username, password):
        try:
            response = requests.post(
                API_LOGIN_URL,
                data={"username": username, "password": password},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("access") or response.json().get("token")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur login : {e}"))
            return None

    def fetch_image(self, name, query):
        try:
            response = requests.get(
                UNSPLASH_URL,
                params={"query": query, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                timeout=10
            )
            response.raise_for_status()
            photo_url = response.json()["urls"]["regular"]

            img_response = requests.get(photo_url, timeout=15)
            img_response.raise_for_status()

            filename = f"{name.lower().replace(' ', '_').replace('&', 'and')}.jpg"
            self.stdout.write(f"🖼  Image téléchargée pour {name}")
            return img_response.content, filename

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Image {name} — {e}"))
            return None, None

    def get_existing_id(self, name, headers):
        """Récupère l'id d'une catégorie existante par son nom."""
        try:
            response = requests.get(
                API_CATEGORIES_URL,
                params={"search": name},
                headers=headers,
                timeout=10
            )
            results = response.json()
            if results:
                return results[0]["id"]
        except Exception:
            pass
        return None