from django.urls import path
from . import views

urlpatterns = [
    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/approval_pending/', views.approval_pending, name='approval_pending'),
    path('login/', views.login, name='login'),
]
