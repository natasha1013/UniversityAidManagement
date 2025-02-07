from django.urls import path
from . import views

app_name = 'notifications'  # Define the namespace here

urlpatterns = [
    path('', views.notification_list, name='notification_list'),  # Ensure this line is correct
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
]