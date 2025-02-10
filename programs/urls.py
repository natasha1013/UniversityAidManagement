from django.urls import path
from .views import aid_list, aid_details, apply_for_aid, application_status_view, manage_aid_applications, review_application, propose_aid_program, review_aid_program, approve_aid, reject_aid



urlpatterns = [
    path('aid/', aid_list, name='aid_list'),
    path('aid/<int:aid_id>/', aid_details, name='aid_details'),
    path('aid/<int:aid_id>/apply/', apply_for_aid, name='apply_for_aid'),
    path('applications/', application_status_view, name='application_status_view'),
    path('manage/', manage_aid_applications, name='manage_aid_applications'),

   # path('manage/<int:application_id>/', review_application, name='review_application'),
   
    path("propose_aid/", propose_aid_program, name="propose_aid"),
    path("review_aid_program/", review_aid_program, name="review_aid_program"),
    path("approve_aid/<int:aid_id>/", approve_aid, name="approve_aid"),
    path("reject_aid/<int:aid_id>/", reject_aid, name="reject_aid"),
]