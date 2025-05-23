# Generated by Django 5.2 on 2025-04-28 15:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_project_college_centered'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='final_priority',
            field=models.IntegerField(blank=True, help_text='Project ranking (lower number = higher priority)', null=True),
        ),
        migrations.CreateModel(
            name='ProjectScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategic_alignment', models.IntegerField(blank=True, help_text='Strategic alignment score (1-5)', null=True)),
                ('cost_benefit', models.IntegerField(blank=True, help_text='Cost benefit score (1-5)', null=True)),
                ('user_impact', models.IntegerField(blank=True, help_text='User impact and adoption score (1-5)', null=True)),
                ('ease_of_implementation', models.IntegerField(blank=True, help_text='Ease of implementation score (1-5)', null=True)),
                ('vendor_reputation_support', models.IntegerField(blank=True, help_text='Vendor reputation and support score (1-5)', null=True)),
                ('security_compliance', models.IntegerField(blank=True, help_text='Security and compliance score (1-5)', null=True)),
                ('student_centered', models.IntegerField(blank=True, help_text='Student-centered score (1-5)', null=True)),
                ('college_centered', models.IntegerField(blank=True, help_text='College-centered score (1-5)', null=True)),
                ('scoring_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='projects.project')),
                ('scored_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('project', 'scored_by')},
            },
        ),
    ]
