import requests
from django.core.management.base import BaseCommand

from api.models import Category


class Command(BaseCommand):
    help = (
        "Réutilise les images déjà en local (MinIO) pour compléter des catégories "
        "existant sur une autre cible (typiquement la prod) mais sans image — utile "
        "après un déploiement, quand des catégories ont été créées avant que le "
        "correctif d'upload soit en ligne. Ne consomme aucun quota Unsplash."
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username admin sur la cible')
        parser.add_argument('--password', type=str, required=True, help='Password admin sur la cible')
        parser.add_argument(
            '--api-url', type=str, required=True,
            help="Base URL de la cible à compléter (ex: https://api.skillou.com)"
        )
        parser.add_argument(
            '--only-missing', action='store_true', default=True,
            help="Ne touche que les catégories cibles dont l'image est vide (comportement par défaut)"
        )

    def handle(self, *args, **options):
        base_url = options['api_url'].rstrip('/')
        login_url = f"{base_url}/api/token"
        categories_url = f"{base_url}/category/"

        token = self.get_token(login_url, options['username'], options['password'])
        if not token:
            self.stdout.write(self.style.ERROR(f"❌ Authentification échouée sur {base_url}."))
            return

        headers = {"Authorization": f"Bearer {token}"}

        self.stdout.write("📥 Récupération de l'arborescence des catégories cibles...")
        remote_by_name = self.fetch_remote_tree(categories_url, headers)
        self.stdout.write(f"   {len(remote_by_name)} catégories trouvées sur {base_url}")

        success, skipped, failed = 0, 0, 0

        for cat in Category.objects.all().order_by('id'):
            remote = remote_by_name.get(cat.name)
            if not remote:
                self.stdout.write(self.style.WARNING(f"⏭  {cat.name} — absente sur {base_url}, ignorée"))
                skipped += 1
                continue

            if remote.get("image") and options['only_missing']:
                self.stdout.write(f"⏭  {cat.name} — a déjà une image sur {base_url}")
                skipped += 1
                continue

            if not cat.image:
                self.stdout.write(self.style.WARNING(f"⏭  {cat.name} — pas d'image en local non plus"))
                skipped += 1
                continue

            try:
                cat.image.open('rb')
                content = cat.image.read()
                cat.image.close()
                filename = cat.image.name.rsplit('/', 1)[-1]

                response = requests.patch(
                    f"{categories_url}{remote['id']}/",
                    files={"image_upload": (filename, content, "image/jpeg")},
                    headers=headers,
                    timeout=15,
                )

                if response.status_code == 200 and response.json().get("image"):
                    self.stdout.write(self.style.SUCCESS(f"✅ {cat.name} (id={remote['id']})"))
                    success += 1
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ {cat.name} — {response.status_code} : {response.text}"
                    ))
                    failed += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {cat.name} — {e}"))
                failed += 1

        self.stdout.write("\n─────────────────────────────")
        self.stdout.write(self.style.SUCCESS(f"✅  Complétées : {success}"))
        self.stdout.write(self.style.WARNING(f"⏭  Ignorées   : {skipped}"))
        self.stdout.write(self.style.ERROR  (f"❌  Échecs     : {failed}"))

    def get_token(self, login_url, username, password):
        try:
            response = requests.post(login_url, data={"username": username, "password": password}, timeout=10)
            response.raise_for_status()
            return response.json().get("access") or response.json().get("token")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur login sur {login_url} : {e}"))
            return None

    def fetch_remote_tree(self, categories_url, headers):
        """
        Construit un dict {name: {"id":..., "image":...}} pour toutes les catégories
        de la cible (racines + enfants), en paginant sur le listing racine et en
        utilisant l'action `children` pour chaque racine.
        """
        by_name = {}

        url = categories_url
        while url:
            resp = requests.get(url, headers=headers, timeout=15).json()
            for root in resp.get("results", []):
                by_name[root["name"]] = {"id": root["id"], "image": root.get("image")}

                children = requests.get(
                    f"{categories_url}{root['id']}/children/", headers=headers, timeout=15
                ).json()
                for child in children:
                    by_name[child["name"]] = {"id": child["id"], "image": child.get("image")}

            url = resp.get("next")

        return by_name
