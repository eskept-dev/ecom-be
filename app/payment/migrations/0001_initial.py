# Generated by Django 5.1.7 on 2025-06-22 11:51

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('booking', '0008_remove_booking_payment_method_delete_paymentmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash')], max_length=32, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('new', 'New'), ('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='new', max_length=32)),
                ('payment_method_type', models.CharField(choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash')], db_column='payment_method_type', default='credit_card', max_length=32)),
                ('transaction_code', models.CharField(blank=True, max_length=64, null=True)),
                ('transaction_time', models.DateTimeField(blank=True, null=True)),
                ('success_time', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16)),
                ('currency', models.CharField(default='VND', max_length=8)),
                ('buyer_name', models.CharField(max_length=128)),
                ('buyer_email', models.EmailField(max_length=254)),
                ('buyer_phone', models.CharField(max_length=20)),
                ('buyer_address', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer_city', models.CharField(blank=True, max_length=128, null=True)),
                ('buyer_country', models.CharField(blank=True, max_length=128, null=True)),
                ('installment', models.BooleanField(default=False)),
                ('installment_month', models.IntegerField(blank=True, null=True)),
                ('bank_code', models.CharField(blank=True, max_length=32, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=128, null=True)),
                ('card_number', models.CharField(blank=True, max_length=32, null=True)),
                ('payer_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('merchant_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('authen_code', models.CharField(blank=True, max_length=64, null=True)),
                ('bank_type', models.CharField(blank=True, max_length=32, null=True)),
                ('signature', models.TextField(blank=True, null=True)),
                ('checksum', models.TextField(blank=True, null=True)),
                ('request_payload', models.JSONField(blank=True, null=True)),
                ('response_payload', models.JSONField(blank=True, null=True)),
                ('webhook_payload', models.JSONField(blank=True, null=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_transactions', to='booking.booking')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
