# Plan — Système de disponibilités & nouveau parcours d'invitation

## Contexte

Simplifier le parcours d'invitation en intégrant la planification dès l'envoi.
L'envoyeur choisit un créneau dans les disponibilités du destinataire → le destinataire n'a plus qu'à dire oui ou non.

### Avant
1. Envoyer une invitation
2. Le destinataire accepte ou refuse
3. L'un propose une date/heure (`propose_schedule`)
4. L'autre confirme le RDV (`confirm_schedule`)
5. La séance a lieu
6. Les deux valident

### Après
1. Envoyer une invitation **avec un créneau déjà choisi**
2. Le destinataire accepte ou refuse
3. La séance a lieu
4. Les deux valident

---

## Étape 1 — Nouveau modèle `Availability`

**Fichier à créer :** `icanhelp/api/models/Availability.py`

```python
class PlaceType(models.TextChoices):
    IN_PERSON = "IN_PERSON", "En personne"
    ONLINE    = "ONLINE",    "En ligne"
    FLEXIBLE  = "FLEXIBLE",  "Flexible"

class Availability(models.Model):
    user      = models.ForeignKey('api.UserProfil', related_name='availabilities', on_delete=models.CASCADE)
    dayOfWeek = models.IntegerField()        # 0 = lundi, 6 = dimanche
    startTime = models.TimeField()
    endTime   = models.TimeField()
    placeType = models.CharField(max_length=20, choices=PlaceType.choices, default=PlaceType.FLEXIBLE)
    place     = models.CharField(max_length=255, blank=True, null=True)   # adresse si IN_PERSON
    link      = models.CharField(max_length=500, blank=True, null=True)   # lien Meet/Zoom si ONLINE

    class Meta:
        ordering = ['dayOfWeek', 'startTime']
```

Exporter depuis `icanhelp/api/models/__init__.py`.

---

## Étape 2 — Migration Availability

Générer la migration :
```
python manage.py makemigrations
```

---

## Étape 3 — Modifications du modèle `Invitation`

**Fichier :** `icanhelp/api/models/Invitation.py`

### 3a. Supprimer l'état `SCHEDULED`

```python
# Avant
class InvitationState(models.TextChoices):
    PENDING   = "PENDING",   "En attente"
    ACCEPTED  = "ACCEPT",    "Accepté"
    REJECTED  = "REJECT",    "Refusé"
    VALIDATED = "VALIDATE",  "Terminé"
    SCHEDULED = "SCHEDULED", "RDV confirmé"   # ← supprimer

# Après
class InvitationState(models.TextChoices):
    PENDING   = "PENDING",  "En attente"
    ACCEPTED  = "ACCEPT",   "Accepté"
    REJECTED  = "REJECT",   "Refusé"
    VALIDATED = "VALIDATE", "Terminé"
```

### 3b. Rendre `scheduledAt` obligatoire

```python
# Avant
scheduledAt = models.DateTimeField(blank=True, null=True)

# Après
scheduledAt = models.DateTimeField()
```

### 3c. Supprimer `scheduledBy`

Supprimer le champ :
```python
scheduledBy = models.ForeignKey(...)   # ← supprimer
```

### Migration associée

La migration doit :
- Rendre `scheduledAt` NOT NULL (fixer une valeur par défaut pour les lignes existantes, ex. `timezone.now()`)
- Supprimer la colonne `scheduledBy_id`
- Migrer les invitations `SCHEDULED` existantes vers `ACCEPT`

```python
# Dans la migration, avant d'appliquer les contraintes :
migrations.RunSQL(
    "UPDATE api_invitation SET state = 'ACCEPT' WHERE state = 'SCHEDULED';"
)
migrations.RunSQL(
    "UPDATE api_invitation SET scheduled_at = NOW() WHERE scheduled_at IS NULL;"
)
```

---

## Étape 4 — Sérialiseurs

**Fichier :** `icanhelp/api/serializers.py`

### 4a. Nouveau `AvailabilitySerializer`

```python
class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'
        read_only_fields = ['user']
```

### 4b. Mettre à jour `CreateInvitationSerializer`

```python
# Avant
fields = ['id', 'receiver', 'createdBy', 'competence', 'points', 'duration', 'message', 'discussion', 'type']

# Après — ajouter scheduledAt (obligatoire) et scheduledPlace (optionnel)
fields = ['id', 'receiver', 'createdBy', 'competence', 'points', 'duration',
          'message', 'discussion', 'type', 'scheduledAt', 'scheduledPlace']
```

---

## Étape 5 — Nouveau ViewSet `AvailabilityViewSet`

**Fichier à créer :** `icanhelp/api/views/availability.py`

```python
class AvailabilityViewSet(UserProfilMixin, viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            # Consulter les dispos d'un autre utilisateur (formulaire d'envoi)
            return Availability.objects.filter(user__id=user_id)
        # Ses propres dispos
        return Availability.objects.filter(user=self.get_user_profil())

    def perform_create(self, serializer):
        serializer.save(user=self.get_user_profil())
```

Exporter depuis `icanhelp/api/views/__init__.py`.

---

## Étape 6 — Mise à jour des vues `invitation.py`

**Fichier :** `icanhelp/api/views/invitation.py`

### 6a. `create()` — rendre `scheduledAt` obligatoire

```python
scheduled_at = request.data.get('scheduledAt')
if not scheduled_at:
    return api_error(ErrorCode.SCHEDULE_DATE_REQUIRED, "Le créneau est obligatoire pour envoyer une invitation.")
```

Passer `scheduledAt` et `scheduledPlace` dans le serializer :
```python
serializer = CreateInvitationSerializer(data={
    **request.data,
    'createdBy': user_profil.id,
    ...
    'scheduledAt':    request.data.get('scheduledAt'),
    'scheduledPlace': request.data.get('scheduledPlace'),
})
```

### 6b. `accept()` — ajouter la logique de conflit

```python
with transaction.atomic():
    invitation.state = InvitationState.ACCEPTED
    invitation.save()
    invitation.createdBy.accept_invitation(invitation)
    invitation.receiver.accept_invitation(invitation)

    # Auto-rejeter les autres invitations en attente sur le même créneau
    conflicting = Invitation.objects.filter(
        receiver=invitation.receiver,
        state=InvitationState.PENDING,
        scheduledAt=invitation.scheduledAt,
    ).exclude(pk=invitation.pk)
    conflicting.update(state=InvitationState.REJECTED)
    # TODO: notifier les envoyeurs concernés ("Ce créneau vient d'être pris")
```

### 6c. `validate()` — changer le check d'état

```python
# Avant
if invitation.state != InvitationState.SCHEDULED:

# Après
if invitation.state != InvitationState.ACCEPTED:
```

### 6d. `reject()` — retirer `SCHEDULED` de la liste

```python
# Avant
if invitation.state not in [InvitationState.PENDING, InvitationState.ACCEPTED, InvitationState.SCHEDULED]:
    ...
if invitation.state in [InvitationState.ACCEPTED, InvitationState.SCHEDULED]:
    ...

# Après
if invitation.state not in [InvitationState.PENDING, InvitationState.ACCEPTED]:
    ...
if invitation.state == InvitationState.ACCEPTED:
    ...
```

### 6e. Supprimer les actions obsolètes

- Supprimer `propose_schedule()`
- Supprimer `confirm_schedule()`

---

## Étape 7 — URLs

**Fichier :** `icanhelp/icanhelp/urls.py`

```python
from api.views.availability import AvailabilityViewSet

router.register(r'availabilities', AvailabilityViewSet, basename='availability')
```

---

## Étape 8 — Erreurs

**Fichier :** `icanhelp/api/utils/errors.py`

Vérifier que `SCHEDULE_DATE_REQUIRED` existe, sinon l'ajouter.

---

## Récapitulatif des endpoints après implémentation

| Méthode | URL | Description |
|---|---|---|
| GET | `/availabilities/` | Mes disponibilités |
| GET | `/availabilities/?user_id=X` | Dispos d'un autre utilisateur |
| POST | `/availabilities/` | Créer un créneau |
| PUT/PATCH | `/availabilities/{id}/` | Modifier un créneau |
| DELETE | `/availabilities/{id}/` | Supprimer un créneau |
| POST | `/invitations/` | Envoyer une invitation (scheduledAt obligatoire) |
| POST | `/invitations/{id}/accept/` | Accepter (+ conflit auto-rejeté) |
| POST | `/invitations/{id}/reject/` | Refuser |
| POST | `/invitations/{id}/validate/` | Valider après séance |

**Supprimés :**
- `POST /invitations/{id}/propose_schedule/`
- `POST /invitations/{id}/confirm_schedule/`

---

## Ordre d'implémentation

- [x] Étape 1 — Modèle `Availability`
- [x] Étape 2 — Migration `Availability` (0021_availability_and_invitation_v2.py)
- [x] Étape 3 — Modèle `Invitation` (supprimer `SCHEDULED`, rendre `scheduledAt` obligatoire, supprimer `scheduledBy`) + migration
- [x] Étape 4 — Sérialiseurs (`AvailabilitySerializer`, update `CreateInvitationSerializer`)
- [x] Étape 5 — ViewSet `AvailabilityViewSet`
- [x] Étape 6 — Vues `invitation.py` (supprimer `propose_schedule`/`confirm_schedule`, update `validate`/`reject`, ajouter conflit dans `accept`, rendre `scheduledAt` obligatoire dans `create`)
- [x] Étape 7 — URLs
- [x] Étape 8 — Erreurs (SCHEDULE_DATE_REQUIRED existait déjà)
