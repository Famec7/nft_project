# Generated by Django 4.2.20 on 2025-04-25 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.IntegerField()),
                ('item_id', models.IntegerField()),
                ('seller', models.CharField(max_length=42)),
                ('price_klay', models.DecimalField(decimal_places=6, max_digits=18)),
                ('metadata_uri', models.CharField(max_length=255)),
                ('is_listed', models.BooleanField(default=False)),
                ('listing_duration', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
