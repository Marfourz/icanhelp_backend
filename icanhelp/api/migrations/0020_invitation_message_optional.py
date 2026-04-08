from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_unique_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='message',
            field=models.TextField(blank=True, default=''),
        ),
    ]
