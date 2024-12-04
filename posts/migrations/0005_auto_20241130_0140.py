# Generated by Django 3.1.12 on 2024-11-30 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20241130_0137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='cover_photo',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='cover_picture',
            field=models.ImageField(blank=True, null=True, upload_to='cover_pictures/'),
        ),
    ]