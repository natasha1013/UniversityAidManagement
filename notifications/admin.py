# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, SystemLog

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at', 'mark_as_read_button')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)
    list_per_page = 25

    # Custom action to mark selected notifications as read
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Mark selected notifications as read"

    # Add the custom action to the admin
    actions = [mark_as_read]

    # Custom method to display a button in the list view
    def mark_as_read_button(self, obj):
        if not obj.read:
            return format_html('<a href="/admin/your_app/notification/{}/change/?read=True" class="button">Mark as Read</a>', obj.id)
        return "Already Read"
    mark_as_read_button.short_description = 'Action'

# Register the Notification model with the custom admin class
admin.site.register(Notification, NotificationAdmin)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'description', 'user', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('description', 'user__username')
    readonly_fields = ('action_type', 'description', 'user', 'timestamp')  # Make fields read-only

    def has_add_permission(self, request):
        return False  # Prevent admins from manually adding logs

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent admins from deleting logs