# Generated by Django 4.2.8 on 2024-01-21 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardiograf', '0007_kardiografuser_numberphone'),
    ]

    operations = [
        migrations.AddField(
            model_name='kardiografuser',
            name='imageUser',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]