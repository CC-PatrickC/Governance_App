from django import forms
from .models import Project, ProjectFile

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'project_type', 'priority', 'status', 'department', 'triage_notes', 'scoring_notes', 'final_priority', 'final_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'triage_notes': forms.Textarea(attrs={'rows': 4}),
            'scoring_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_files(self):
        files = self.files.getlist('files')
        if len(files) > 5:
            raise forms.ValidationError("You can upload a maximum of 5 files.")
        return files 