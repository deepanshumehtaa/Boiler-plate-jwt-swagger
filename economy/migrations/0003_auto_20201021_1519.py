# Generated by Django 3.1.2 on 2020-10-21 15:19

from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ('economy', '0002_auto_20200228_2132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productorder',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='productorder',
            name='purchase',
        ),
        migrations.AddField(
            model_name='productorder',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_orders', to='economy.socisession'),
        ),
        migrations.AddField(
            model_name='productorder',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_orders', to='economy.socibankaccount'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='economy.socisession'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='economy.socibankaccount'),
        ),
    ]
