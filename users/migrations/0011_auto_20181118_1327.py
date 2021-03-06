# Generated by Django 2.1.2 on 2018-11-18 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20181118_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersHaveMadeOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='made_out_with_left_side', to=settings.AUTH_USER_MODEL)),
                ('user_two', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='made_out_with_right_side', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='have_made_out_with',
            field=models.ManyToManyField(related_name='users', through='users.UsersHaveMadeOut', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='usershavemadeout',
            index=models.Index(fields=['user_one', 'user_two'], name='users_users_user_on_be886d_idx'),
        ),
        migrations.AddIndex(
            model_name='usershavemadeout',
            index=models.Index(fields=['user_two', 'user_one'], name='users_users_user_tw_8b64d8_idx'),
        ),
    ]
