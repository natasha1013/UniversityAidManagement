# feedbacks/admin.py
from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('title', 'sender', 'receiver', 'category', 'is_read', 'created_at')

    # Add search functionality (e.g., search by title, sender, or receiver)
    search_fields = ('title', 'sender__username', 'receiver__username')

    # Add filters for quick navigation (e.g., filter by category or read status)
    list_filter = ('category', 'is_read', 'created_at')

    # Make certain fields editable directly in the list view
    list_editable = ('is_read',)

    # Order feedback by creation date (newest first)
    ordering = ('-created_at',)