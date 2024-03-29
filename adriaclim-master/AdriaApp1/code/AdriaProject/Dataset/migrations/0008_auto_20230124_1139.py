# Generated by Django 3.2.4 on 2023-01-24 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dataset', '0007_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='dimension_names',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AddField(
            model_name='indicator',
            name='dimensions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='indicator',
            name='variable_names',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AddField(
            model_name='indicator',
            name='variables',
            field=models.IntegerField(default=0),
        ),
    ]
