from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0034_add_triage_change_model'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='contact_person',
            new_name='technician',
        ),
    ]

