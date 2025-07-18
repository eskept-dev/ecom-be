# Generated by Django 5.1.7 on 2025-07-18 04:15

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_product_max_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price_usd',
            new_name='base_price_usd',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='price_vnd',
            new_name='base_price_vnd',
        ),
        migrations.CreateModel(
            name='ProductAvailabilityConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=255, unique=True)),
                ('type', models.CharField(choices=[('block', 'Block'), ('no_limit', 'No Limit'), ('fixed_quantity', 'Fixed Quantity'), ('percentage_quantity', 'Percentage Quantity')], max_length=255)),
                ('value', models.IntegerField()),
                ('day', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_configs', to='product.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductPriceConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('adjustment_type', models.CharField(choices=[('fixed', 'Fixed'), ('percentage', 'Percentage')], default='fixed', max_length=32)),
                ('adjustment_value', models.JSONField(blank=True, null=True)),
                ('time_range_type', models.CharField(choices=[('period', 'Period'), ('recurring_day_of_week', 'Recurring Day Of Week'), ('recurring_day_of_month', 'Recurring Day Of Month')], default='period', max_length=32)),
                ('time_range_value', models.JSONField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('products', models.ManyToManyField(blank=True, related_name='price_configs', to='product.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
