# Generated by Django 5.1.7 on 2025-06-02 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_product_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='available_locations',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
