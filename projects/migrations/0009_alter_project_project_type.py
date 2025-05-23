# Generated by Django 5.2 on 2025-04-10 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_project_project_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.CharField(choices=[('not_yet_decided', 'Not Yet Decided'), ('process_improvement', 'Process Improvement'), ('it_governance', 'IT Governance'), ('erp_governance', 'ERP Governance'), ('data_governance', 'Data Governance')], default='not_yet_decided', help_text='Type of project submission', max_length=20),
        ),
    ]
