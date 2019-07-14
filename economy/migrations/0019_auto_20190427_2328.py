# Generated by Django 2.2 on 2019-04-27 23:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models, connection

import economy.models


class Migration(migrations.Migration):
    # Without this, the following error was produced:
    # ```
    # django.db.utils.NotSupportedError: Renaming the 'economy_purchasecollection' table while in a transaction is not
    # supported on SQLite < 3.26 because it would break referential integrity. Try adding `atomic = False` to the
    # Migration class.
    # ```
    if connection.vendor == 'sqlite':
        atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('economy', '0018_auto_20190422_1627'),
    ]

    operations = [
        # Renaming
        migrations.RenameModel(
            old_name='PurchaseCollection',
            new_name='SociSession',
        ),
        migrations.RenameField(
            model_name='purchase',
            old_name='collection',
            new_name='session',
        ),

        # Adding
        migrations.AddField(
            model_name='socisession',
            name='signed_off_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    to=settings.AUTH_USER_MODEL),
        ),

        # Altering
        migrations.AlterField(
            model_name='purchase',
            name='session',
            field=models.ForeignKey(default=economy.models.SociSession.get_active_session,
                                    on_delete=django.db.models.deletion.DO_NOTHING, related_name='purchases',
                                    to='economy.SociSession'),
        ),
        migrations.AlterField(
            model_name='sociproduct',
            name='icon',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),

        # Removing
        migrations.RemoveField(
            model_name='purchase',
            name='signed_off_by',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='signed_off_time',
        ),
        migrations.RemoveField(
            model_name='socibankaccount',
            name='display_balance_at_soci',
        ),
    ]
