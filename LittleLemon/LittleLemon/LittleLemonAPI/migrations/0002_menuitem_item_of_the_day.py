# Generated by Django 5.2 on 2025-04-11 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='item_of_the_day',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
