# Generated by Django 3.2.4 on 2023-10-24 08:04

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('dataset_id', models.CharField(default='', max_length=500, primary_key=True, serialize=False)),
                ('adriaclim_dataset', models.CharField(default='', max_length=500)),
                ('adriaclim_model', models.CharField(default='', max_length=500)),
                ('adriaclim_timeperiod', models.CharField(default='', max_length=500)),
                ('adriaclim_scale', models.CharField(default='', max_length=500)),
                ('adriaclim_type', models.CharField(default='', max_length=500)),
                ('title', models.CharField(max_length=1500)),
                ('metadata_url', models.CharField(default='', max_length=1500)),
                ('institution', models.CharField(default='', max_length=300)),
                ('lat_min', models.CharField(default='', max_length=300, null=True)),
                ('lat_max', models.CharField(default='', max_length=300, null=True)),
                ('lng_min', models.CharField(default='', max_length=300, null=True)),
                ('lng_max', models.CharField(default='', max_length=300, null=True)),
                ('param_min', models.FloatField(default=0, null=True)),
                ('param_max', models.FloatField(default=0, null=True)),
                ('param_step', models.FloatField(default=0, null=True)),
                ('time_start', models.CharField(default='', max_length=120)),
                ('time_end', models.CharField(default='', max_length=120)),
                ('tabledap_url', models.CharField(default='', max_length=250)),
                ('dimensions', models.IntegerField(default=0, null=True)),
                ('dimension_names', models.CharField(default='', max_length=1500, null=True)),
                ('variables', models.IntegerField(default=0, null=True)),
                ('variable_names', models.CharField(default='', max_length=1500, null=True)),
                ('variable_types', models.CharField(default='', max_length=250, null=True)),
                ('griddap_url', models.CharField(default='', max_length=250, null=True)),
                ('wms_url', models.CharField(default='', max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.CharField(default='', max_length=500, primary_key=True, serialize=False)),
                ('adriaclim_dataset', models.CharField(default='', max_length=500)),
                ('adriaclim_model', models.CharField(default='', max_length=500)),
                ('adriaclim_timeperiod', models.CharField(default='', max_length=500)),
                ('adriaclim_scale', models.CharField(default='', max_length=500)),
                ('adriaclim_type', models.CharField(default='', max_length=500)),
                ('title', models.CharField(max_length=1500)),
                ('metadata_url', models.CharField(default='', max_length=1500)),
                ('institution', models.CharField(default='', max_length=300)),
                ('lat_min', models.CharField(default='', max_length=300, null=True)),
                ('lat_max', models.CharField(default='', max_length=300, null=True)),
                ('lng_min', models.CharField(default='', max_length=300, null=True)),
                ('lng_max', models.CharField(default='', max_length=300, null=True)),
                ('time_start', models.CharField(default='', max_length=120)),
                ('time_end', models.CharField(default='', max_length=120)),
                ('param_min', models.FloatField(default=0, null=True)),
                ('param_max', models.FloatField(default=0, null=True)),
                ('param_step', models.FloatField(default=0, null=True)),
                ('tabledap_url', models.CharField(default='', max_length=250)),
                ('dimensions', models.IntegerField(default=0, null=True)),
                ('dimension_names', models.CharField(default='', max_length=1500, null=True)),
                ('variables', models.IntegerField(default=0, null=True)),
                ('variable_names', models.CharField(default='', max_length=1500, null=True)),
                ('variable_types', models.CharField(default='', max_length=250, null=True)),
                ('griddap_url', models.CharField(default='', max_length=250, null=True)),
                ('wms_url', models.CharField(default='', max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Polygon',
            fields=[
                ('pol_vertices_str', models.CharField(default='', max_length=500, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value_0', models.FloatField(default=None, null=True)),
                ('value_1', models.FloatField(default=None, null=True)),
                ('value_2', models.FloatField(default=None, null=True)),
                ('value_3', models.FloatField(default=None, null=True)),
                ('value_4', models.FloatField(default=None, null=True)),
                ('value_5', models.FloatField(default=None, null=True)),
                ('value_6', models.FloatField(default=None, null=True)),
                ('value_7', models.FloatField(default=None, null=True)),
                ('value_8', models.FloatField(default=None, null=True)),
                ('value_9', models.FloatField(default=None, null=True)),
                ('value_10', models.FloatField(default=None, null=True)),
                ('value_11', models.FloatField(default=None, null=True)),
                ('value_12', models.FloatField(default=None, null=True)),
                ('value_13', models.FloatField(default=None, null=True)),
                ('value_14', models.FloatField(default=None, null=True)),
                ('value_15', models.FloatField(default=None, null=True)),
                ('value_16', models.FloatField(default=None, null=True)),
                ('value_17', models.FloatField(default=None, null=True)),
                ('value_18', models.FloatField(default=None, null=True)),
                ('value_19', models.FloatField(default=None, null=True)),
                ('value_20', models.FloatField(default=None, null=True)),
                ('value_21', models.FloatField(default=None, null=True)),
                ('value_22', models.FloatField(default=None, null=True)),
                ('value_23', models.FloatField(default=None, null=True)),
                ('value_24', models.FloatField(default=None, null=True)),
                ('value_25', models.FloatField(default=None, null=True)),
                ('date_value', models.CharField(default='', max_length=500, null=True)),
                ('latitude', models.FloatField(default=0, null=True)),
                ('longitude', models.FloatField(default=0, null=True)),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('parametro_agg', models.CharField(default='', max_length=500, null=True)),
                ('dataset_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Dataset.node')),
            ],
        ),
    ]
