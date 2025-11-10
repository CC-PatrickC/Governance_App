from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'status', 'submitted_by', 'submission_date')
    list_filter = ('status', 'department', 'submission_date')
    search_fields = ('title', 'description', 'department', 'technician')
    date_hierarchy = 'submission_date'
    ordering = ('-submission_date',)
