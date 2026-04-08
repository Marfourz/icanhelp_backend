from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_fix_userdiscussionmetadata'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE auth_user ADD UNIQUE INDEX unique_user_email (email);",
            reverse_sql="ALTER TABLE auth_user DROP INDEX unique_user_email;",
        ),
    ]
