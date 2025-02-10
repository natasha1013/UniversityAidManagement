from django.contrib import admin
from .models import *

# Admin configuration for the AidProgram model
class AidProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'aid_type', 'level', 'locality', 'status', 'closing_date')
    list_filter = ('status', 'level', 'locality')
    search_fields = ('name', 'owner', 'aid_type')
    ordering = ('-closing_date',)
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'aid_type', 'level', 'locality', 'status', 'closing_date')
        }),
        ('Additional Information', {
            'fields': ('eligibility', 'required_documents', 'total_funds'),
            'classes': ('collapse',),
        }),
    )

# Admin configuration for the ApplicationStatus model
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'aid_program', 'status', 'last_update', 'allocated_funds')
    list_filter = ('status', 'aid_program__name', 'last_update')
    search_fields = ('student__username', 'aid_program__name', 'status')
    ordering = ('-last_update',)
    readonly_fields = ('last_update',)
    fieldsets = (
        (None, {
            'fields': ('aid_program', 'student', 'status', 'last_update')
        }),
        ('Supporting Information', {
            'fields': ('supporting_document', 'officer_comment', 'allocated_funds'),
            'classes': ('collapse',),
        }),
    )

# Admin configuration for the AppealStatus model
class AppealStatusAdmin(admin.ModelAdmin):
    list_display = ('application', 'appeal_status', 'appeal_date')
    list_filter = ('appeal_status', 'appeal_date')
    search_fields = ('application__aid_program__name', 'appeal_status')
    ordering = ('-appeal_date',)
    readonly_fields = ('appeal_date',)
    fieldsets = (
        (None, {
            'fields': ('application', 'appeal_reason', 'appeal_status', 'appeal_date')
        }),
    )

# Register the models with their respective admin configurations
admin.site.register(AidProgram, AidProgramAdmin)
admin.site.register(ApplicationStatus, ApplicationStatusAdmin)
admin.site.register(AppealStatus, AppealStatusAdmin)