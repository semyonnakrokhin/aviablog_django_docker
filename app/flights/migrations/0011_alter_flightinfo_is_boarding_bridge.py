# Generated by Django 4.2 on 2023-07-26 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0010_alter_usertrip_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightinfo',
            name='is_boarding_bridge',
            field=models.BooleanField(default=False, verbose_name='Через телетрап'),
        ),
    ]
