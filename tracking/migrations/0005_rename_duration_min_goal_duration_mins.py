# Generated by Django 4.2.1 on 2023-06-07 04:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tracking", "0004_alter_session_goal"),
    ]

    operations = [
        migrations.RenameField(
            model_name="goal",
            old_name="duration_min",
            new_name="duration_mins",
        ),
    ]
