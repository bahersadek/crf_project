# Generated by Django 4.1.2 on 2022-10-29 18:30

import crapp.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('c_id', models.AutoField(primary_key=True, serialize=False)),
                ('c_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('p_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('details', models.TextField(max_length=2000)),
                ('target', models.PositiveIntegerField()),
                ('start_date', models.DateTimeField(default=datetime.datetime.now)),
                ('end_date', models.DateTimeField(default=crapp.models.get_next_30_days_date)),
                ('creation_date', models.DateTimeField(default=datetime.datetime.now)),
                ('is_featured', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crapp.category')),
                ('owner', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='Projects', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectReports',
            fields=[
                ('r_id', models.AutoField(primary_key=True, serialize=False)),
                ('report', models.TextField(max_length=2000)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crapp.projects')),
                ('reporter', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectPictures',
            fields=[
                ('picture_id', models.AutoField(primary_key=True, serialize=False)),
                ('picture_label', models.CharField(max_length=50)),
                ('picture', models.ImageField(upload_to='project_pics')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crapp.projects')),
            ],
        ),
        migrations.CreateModel(
            name='DonationFund',
            fields=[
                ('d_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.PositiveIntegerField()),
                ('donator', models.ForeignKey(default=None, on_delete=models.SET(crapp.models.get_set_anon_user), to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crapp.projects')),
            ],
        ),
    ]
