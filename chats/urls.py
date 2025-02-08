from django.urls import path
from .views import chat_view, send_message, stream_messages

urlpatterns = [
    path('', chat_view, name='chat_page'),
    path('send-message/', send_message, name='send_message'),
    path('stream-messages/<int:user_id>/', stream_messages, name='stream_messages'),
]
