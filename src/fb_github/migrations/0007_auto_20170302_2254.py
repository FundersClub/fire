# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 22:54
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fb_github', '0006_auto_20170302_2254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
