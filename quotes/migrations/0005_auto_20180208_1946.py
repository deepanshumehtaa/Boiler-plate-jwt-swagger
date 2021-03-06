# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-08 19:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_quote_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='quoter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='quotes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quote',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_quotes', to=settings.AUTH_USER_MODEL),
        ),
    ]
