# Generated by Django 5.0 on 2023-12-14 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0004_bingoproject'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggestion',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bingo_app.bingoproject'),
        ),
    ]
