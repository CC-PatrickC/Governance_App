from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0037_alter_project_stage_alter_project_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='triage_date',
            field=models.DateTimeField(blank=True, help_text='Date when the request was triaged', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='triaged_by',
            field=models.ForeignKey(blank=True, help_text='Technician assigned during triage', null=True, on_delete=models.SET_NULL, related_name='triaged_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]

