# Generated by Django 5.2 on 2025-04-22 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_project_ease_of_implementation'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='vendor_reputation_support',
            field=models.IntegerField(blank=True, help_text='Vendor reputation and support score (1-5)', null=True),
        ),
    ]
