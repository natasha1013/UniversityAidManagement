from django.urls import include, path
from . import views
from programs.views import review_application, manage_aid_applications, funder_review_applications, funder_approve_application, funder_reject_application


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/approval_pending/', views.approval_pending, name='approval_pending'),
    path('login/', views.login, name='login'),
    
    path('profile/', views.dashboard, name = 'dashboard'),

    path('profile/approve-user/<int:user_id>/', views.approve_user, name = 'approve_user'),
    path('profile/reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    
    path('profile/update-user/<int:user_id>/', views.update_user, name='update_user'),
    path('api/users/<int:user_id>/', views.user_detail_api, name='user_detail_api'),

    path('profile/delete-account/', views.delete_account, name='delete_account'),

    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    
    path('profile/officer-dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('profile/?tab=aid_application/<int:application_id>/', review_application, name='review_application'),
    
    path('profile/funder-dashboard/', views.officer_dashboard, name='funder_dashboard'),
    path('profile/funder-dashboard/approve/<int:application_id>/', views.funder_approve_application, name='funder_approve_application'),
    path('profile/funder-dashboard/reject/<int:application_id>/', views.funder_reject_application, name='funder_reject_application'),
    
    
    path('edit-aid/<int:aid_id>/', views.edit_aid, name='edit_aid'),

]
