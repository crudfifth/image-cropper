# Generated by Django 4.2.10 on 2024-02-09 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_user_is_agreed_to_terms_of_service'),
        ('ihiapp', '0064_annualplanvalues_alter_gatewaystartdate_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annualplanvalues',
            name='company_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='企業'),
        ),
    ]
