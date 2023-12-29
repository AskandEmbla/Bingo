# Generated by Django 5.0 on 2023-12-14 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0003_remove_suggestion_downvotes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BingoProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('project_id', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
