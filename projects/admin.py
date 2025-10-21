from django.contrib import admin
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from .models import Project
=======
from .models import Project, Conversation, SystemNotification
>>>>>>> Stashed changes
=======
from .models import Project, Conversation, SystemNotification
>>>>>>> Stashed changes

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'status', 'submitted_by', 'submission_date')
    list_filter = ('status', 'department', 'submission_date')
    search_fields = ('title', 'description', 'department', 'contact_person')
    date_hierarchy = 'submission_date'
    ordering = ('-submission_date',)
<<<<<<< Updated upstream
=======

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('project', 'created_by', 'created_at', 'is_internal')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('project__title', 'message', 'created_by__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('notification_type', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
