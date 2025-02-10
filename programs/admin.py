from django.contrib import admin
from .models import AidProgram, ApplicationStatus, AppealStatus

# Admin configuration for the AidProgram model
class AidProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'aid_type', 'level', 'locality', 'status', 'closing_date', 'approval_status', 'proposed_by')
    list_filter = ('status', 'level', 'locality', 'approval_status', 'proposed_by')
    search_fields = ('name', 'owner', 'aid_type', 'proposed_by__username')
    ordering = ('-closing_date',)
    readonly_fields = ('proposed_by',)  # Make proposed_by read-only in the admin interface

    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'aid_type', 'level', 'locality', 'status', 'closing_date', 'proposed_by')
        }),
        ('Additional Information', {
            'fields': ('eligibility', 'required_documents', 'total_funds', 'approval_status'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically set the `proposed_by` field to the current user if it's not already set
        if not obj.proposed_by:
            obj.proposed_by = request.user
        super().save_model(request, obj, form, change)

# Admin configuration for the ApplicationStatus model
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'aid_program', 'status', 'last_update', 'aid_officer', 'allocated_funds')
    list_filter = ('status', 'aid_program__name', 'last_update', 'aid_officer')
    search_fields = ('student__username', 'aid_program__name', 'status', 'aid_officer__username')
    ordering = ('-last_update',)
    readonly_fields = ('last_update',)

    fieldsets = (
        (None, {
            'fields': ('aid_program', 'student', 'status', 'last_update', 'aid_officer')
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