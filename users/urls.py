from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/approval_pending/', views.approval_pending, name='approval_pending'),
    path('login/', views.login, name='login'),
    path('test/', views.test, name = 'test'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
