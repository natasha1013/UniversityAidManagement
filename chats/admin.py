from django.contrib import admin
from .models import Chat

# Admin configuration for the Message model
class ChatAdmin(admin.ModelAdmin):
    # Display these fields in the list view of the admin panel
    list_display = ('sender', 'recipient', 'message', 'timestamp')

    # Add filters for sender, recipient, and timestamp
    list_filter = ('sender', 'recipient', 'timestamp')

    # Add search functionality for sender, recipient, and message content
    search_fields = ('sender__username', 'recipient__username', 'message')

    # Make the message and timestamp fields read-only in the admin form
    readonly_fields = ('timestamp',)

    # Customize how the form is displayed in the admin panel
    fieldsets = (
        (None, {
            'fields': ('sender', 'recipient', 'message')
        }),
        ('Additional Info', {
            'fields': ('timestamp',)
        }),
    )

# Register the Message model with the custom admin configuration
admin.site.register(Chat, ChatAdmin)