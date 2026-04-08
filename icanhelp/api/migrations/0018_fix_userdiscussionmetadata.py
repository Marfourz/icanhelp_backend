from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_invitation_scheduledat_invitation_scheduledby_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdiscussionmetadata',
            name='lastOpenDiscussionAt',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterUniqueTogether(
            name='userdiscussionmetadata',
            unique_together={('user', 'discussion')},
        ),
    ]
