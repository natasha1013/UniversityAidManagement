# Generated by Django 5.1.2 on 2025-02-07 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='notification',
            table='notifications_table',
        ),
    ]
