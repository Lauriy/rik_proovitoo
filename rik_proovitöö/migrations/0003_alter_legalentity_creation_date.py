# Generated by Django 5.0.7 on 2024-07-21 07:01

from django.db import migrations, models

import rik_proovitöö.models


class Migration(migrations.Migration):
    dependencies = [
        ('rik_proovitöö', '0002_alter_legalentity_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalentity',
            name='creation_date',
            field=models.DateField(blank=True, null=True, validators=[rik_proovitöö.models.no_future_date]),
        ),
    ]
