# Generated by Django 4.2.5 on 2023-09-21 03:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ihiapp', '0015_alter_dailyeconomicactivityamount_options_and_more'),
        ('users', '0006_user_daily_revenue'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='economic_activity_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ihiapp.economicactivityunit', verbose_name='経済活動単位'),
        ),
    ]
