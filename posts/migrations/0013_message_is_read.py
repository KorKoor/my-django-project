# Generated by Django 5.1.3 on 2024-12-02 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_alter_comment_id_alter_customuser_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]