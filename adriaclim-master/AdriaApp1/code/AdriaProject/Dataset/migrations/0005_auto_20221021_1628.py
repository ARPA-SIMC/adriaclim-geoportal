# Generated by Django 3.2.7 on 2022-10-21 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dataset', '0004_indicator'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='institution',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='indicator',
            name='metadata_url',
            field=models.CharField(default='', max_length=1500),
        ),
        migrations.AddField(
            model_name='indicator',
            name='time_end',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='indicator',
            name='time_start',
            field=models.CharField(default='', max_length=120),
        ),
    ]