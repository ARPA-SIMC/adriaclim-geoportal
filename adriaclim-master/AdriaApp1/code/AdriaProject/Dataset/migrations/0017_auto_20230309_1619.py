# Generated by Django 3.2.4 on 2023-03-09 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dataset', '0016_auto_20230309_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='lat_max',
            field=models.CharField(default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='lat_min',
            field=models.CharField(default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='lng_max',
            field=models.CharField(default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='lng_min',
            field=models.CharField(default='', max_length=300, null=True),
        ),
    ]