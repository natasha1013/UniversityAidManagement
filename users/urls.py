from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/approval_pending/', views.approval_pending, name='approval_pending'),
    path('login/', views.login, name='login'),
    
    path('profile/', views.dashboard, name = 'dashboard'),

    path('profile/approve-user/<int:user_id>/', views.approve_user, name = 'approve_user'),
    path('profile/reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    
    path('profile/update-user/<int:user_id>/', views.update_user, name='update_user'),
    path('api/users/<int:user_id>/', views.user_detail_api, name='user_detail_api'),

    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('test/', views.test, name = 'test'),
]
