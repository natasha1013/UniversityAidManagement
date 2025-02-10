from django.urls import path
from .views import *

urlpatterns = [
    path('aid/', aid_list, name='aid_list'),
    path('aid/<int:aid_id>/', aid_details, name='aid_details'),
    path('aid/<int:aid_id>/apply/', apply_for_aid, name='apply_for_aid'),
    path('applications/', application_status_view, name='application_status_view'),
    path('manage/', manage_aid_applications, name='manage_aid_applications'),
    path('manage/<int:application_id>/', review_application, name='review_application'),
]