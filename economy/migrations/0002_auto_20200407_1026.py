# Generated by Django 2.2.7 on 2020-03-29 15:01
"""
See https://docs.djangoproject.com/en/2.2/ref/migration-operations/#runpython for reference
"""

from django.db import migrations
from ksg_nett.settings import SOCI_MASTER_ACCOUNT_CARD_ID


def forward_create_soci_master_account(apps, schema_editor):
    """
    Creates the instance of the master bank account
    """
    BankAccount = apps.get_model("economy", "SociBankAccount")
    db_alias = schema_editor.connection.alias
    BankAccount.objects.using(db_alias).create(card_uuid=SOCI_MASTER_ACCOUNT_CARD_ID)


def reverse_create_soci_master_account(apps, schema_editor):
    """
    Deletes the instance of the master bank account. This function exists to allow for
    unapplying migrations.
    """
    BankAccount = apps.get_model("economy", "SociBankAccount")
    db_alias = schema_editor.connection.alias
    BankAccount.objects.using(db_alias).filter(card_uuid=SOCI_MASTER_ACCOUNT_CARD_ID).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('economy', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_create_soci_master_account, reverse_create_soci_master_account)
    ]
