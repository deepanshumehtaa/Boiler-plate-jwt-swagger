# Generated by Django 2.1.7 on 2019-02-21 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0008_auto_20181204_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='context',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
