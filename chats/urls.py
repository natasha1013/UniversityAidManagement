from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('send-message/', views.send_message, name='send_message'),
    path('stream-messages/<int:user_id>/', views.stream_messages, name='stream_messages'),
    path('search-users/', views.search_users, name='search_users'),
]
