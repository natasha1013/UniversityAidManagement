# feedbacks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_view, name='feedback_view'),
    path('send/', views.send_feedback, name='send_feedback'),
    path('reply/<int:feedback_id>/', views.reply_feedback, name='reply_feedback'),
]