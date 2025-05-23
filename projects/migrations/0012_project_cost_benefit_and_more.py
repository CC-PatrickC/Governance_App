# Generated by Django 5.2 on 2025-04-22 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_project_strategic_alignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='cost_benefit',
            field=models.IntegerField(blank=True, help_text='Cost benefit score (1-5)', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='strategic_alignment',
            field=models.IntegerField(blank=True, help_text='Strategic alignment score (1-5)', null=True),
        ),
    ]
