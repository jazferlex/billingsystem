# Generated by Django 3.1.3 on 2021-07-05 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0038_meterreadingmodification_accountinfoid'),
    ]

    operations = [
        migrations.AddField(
            model_name='meterreadingmodification',
            name='postedby',
            field=models.CharField(default='', max_length=30),
        ),
    ]
