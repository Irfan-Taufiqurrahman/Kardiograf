# Generated by Django 4.2.8 on 2024-01-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardiograf', '0010_alter_kardiografuser_numberphone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kardiografuser',
            name='birthdate',
            field=models.DateField(null=True),
        ),
    ]