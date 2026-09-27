from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_availability_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('user', 'dayOfWeek', 'startTime', 'endTime')},
        ),
    ]
