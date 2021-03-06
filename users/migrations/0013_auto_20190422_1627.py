# Generated by Django 2.2 on 2019-04-22 16:27

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20181123_2049'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usershavemadeout',
            old_name='created_at',
            new_name='created',
        ),
        migrations.AlterField(
            model_name='usershavemadeout',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='usershavemadeout',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='user',
            name='ksg_role',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='gjengis', max_length=100, no_check_for_status=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='ksg_status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='aktiv', max_length=100, no_check_for_status=True),
        ),
    ]
