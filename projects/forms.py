from django import forms
from .models import Project, ProjectFile

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'contact_person', 'department']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Subject',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make contact_person required
        self.fields['contact_person'].required = True
        self.fields['contact_person'].widget.attrs['required'] = 'required'

    def clean_files(self):
        files = self.files.getlist('files')
        if len(files) > 5:
            raise forms.ValidationError("You can upload a maximum of 5 files.")
        return files 