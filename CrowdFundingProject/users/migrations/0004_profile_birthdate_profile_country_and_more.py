# Generated by Django 4.1.2 on 2022-10-31 13:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(blank=True, choices=[('EG', 'Egypt'), ('UAE', 'United Arab Emirates'), ('UK', 'United Kingdom'), ('USA', 'United States America'), ('CA', 'Canda'), ('SA', 'Saudi Arabia'), ('KW', 'Kuweit')], max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='facebook_url',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
