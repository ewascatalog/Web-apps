# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-16 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20170811_1758'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='results',
            name='dmr',
        ),
        migrations.AddField(
            model_name='results',
            name='details',
            field=models.CharField(blank=True, max_length=200, verbose_name='Details'),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='covariates',
            field=models.CharField(blank=True, max_length=300, verbose_name='Covariates (eg. Age, sex and smoking)'),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='exposure',
            field=models.CharField(max_length=200, verbose_name='Exposure (eg. the Trait)'),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='outcome',
            field=models.CharField(max_length=200, verbose_name='Outcome (eg. DNA methylation)'),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='tissue',
            field=models.CharField(max_length=100, verbose_name='Tissue'),
        ),
        migrations.AlterField(
            model_name='participants',
            name='categories',
            field=models.CharField(blank=True, max_length=200, verbose_name='Categories (eg. 200 smokers, 200 non-smokers)'),
        ),
        migrations.AlterField(
            model_name='results',
            name='beta',
            field=models.CharField(blank=True, max_length=20, verbose_name='Beta'),
        ),
        migrations.AlterField(
            model_name='results',
            name='se',
            field=models.CharField(blank=True, max_length=20, verbose_name='SE'),
        ),
        migrations.AlterField(
            model_name='study',
            name='efo',
            field=models.CharField(blank=True, max_length=50, verbose_name='EFO Term'),
        ),
    ]
