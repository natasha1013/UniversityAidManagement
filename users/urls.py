from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/approval_pending/', views.approval_pending, name='approval_pending'),
    path('login/', views.login, name='login'),
    
    path('profile/', views.dashboard, name = 'dashboard'),

    path('profile/approve-user/', views.pending_users, name = 'pending_users'),
    path('profile/approve-user/<int:user_id>/', views.approve_user, name = 'approve_user'),
    path('profile/reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    
    path('profile/update-user/', views.update_user, name='update_user'),
    path('profile/config-parameters/', views.config_parameters, name='config_parameters'),
    path('profile/add-parameters/', views.add_parameters, name='add_parameters'),
    path('profile/feedback-management/', views.feedback_management, name='feedback_management'),
    path('profile/approve-requests/', views.approve_requests, name='approve_requests'),
    path('profile/edit-program/', views.edit_program, name='edit_program'),

    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('test/', views.test, name = 'test'),
]
