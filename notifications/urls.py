from django.urls import path
from . import views

app_name = 'notifications'  # Define the namespace here

urlpatterns = [
    path('', views.notification_list, name='notification_list'),  # Ensure this line is correct
    path('system-log/', views.system_log_view, name='admin_log'),
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
]