# Generated by Django 3.1.3 on 2021-04-12 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0015_auto_20210412_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicants_info',
            name='profilepic',
            field=models.FileField(default='ui-admin.jpg', upload_to=''),
        ),
    ]
