from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_invitation_message_optional'),
    ]

    operations = [
        # 1. Créer le modèle Availability
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dayOfWeek', models.IntegerField()),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
                ('placeType', models.CharField(
                    choices=[('IN_PERSON', 'En personne'), ('ONLINE', 'En ligne'), ('FLEXIBLE', 'Flexible')],
                    default='FLEXIBLE',
                    max_length=20,
                )),
                ('place', models.CharField(blank=True, max_length=255, null=True)),
                ('link', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='availabilities',
                    to='api.userprofil',
                )),
            ],
            options={
                'ordering': ['dayOfWeek', 'startTime'],
            },
        ),

        # 2. Migrer les invitations SCHEDULED → ACCEPT avant de modifier les contraintes
        migrations.RunSQL(
            "UPDATE api_invitation SET state = 'ACCEPT' WHERE state = 'SCHEDULED';",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 3. Remplir scheduledAt pour les lignes NULL avant de passer en NOT NULL
        migrations.RunSQL(
            "UPDATE api_invitation SET `scheduledAt` = NOW() WHERE `scheduledAt` IS NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 4. Mettre à jour les choix de state (supprimer SCHEDULED)
        migrations.AlterField(
            model_name='invitation',
            name='state',
            field=models.CharField(
                choices=[
                    ('PENDING',   'En attente'),
                    ('ACCEPT',    'Accepté'),
                    ('REJECT',    'Refusé'),
                    ('VALIDATE',  'Terminé'),
                ],
                default='PENDING',
                max_length=20,
            ),
        ),

        # 5. scheduledAt NOT NULL
        migrations.AlterField(
            model_name='invitation',
            name='scheduledAt',
            field=models.DateTimeField(),
        ),

        # 6. Supprimer scheduledBy
        migrations.RemoveField(
            model_name='invitation',
            name='scheduledBy',
        ),
    ]
