# Generated by Django 4.2.8 on 2024-01-13 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardiograf', '0003_kardiografuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='kardiografuser',
            name='role',
            field=models.TextField(blank=True),
        ),
    ]
