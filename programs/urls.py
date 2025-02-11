from django.urls import path
from .views import (aid_list, aid_details, apply_for_aid, application_status_view, manage_aid_applications, review_application, 
                    propose_aid_program, review_aid_program, approve_aid, reject_aid, all_aid_list, my_proposals, funder_review_applications, 
                    funder_approve_application, funder_reject_application, student_fund_utilization, aid_officer_monitor_utilization, flag_fund_utilization,
                    acknowledge_fund_utilization, funder_view_utilization)



urlpatterns = [
    path('aid/', aid_list, name='aid_list'),
    path('aid/<int:aid_id>/', aid_details, name='aid_details'),
    path('aid/<int:aid_id>/apply/', apply_for_aid, name='apply_for_aid'),
    path('applications/', application_status_view, name='application_status_view'),
    path('manage/', manage_aid_applications, name='manage_aid_applications'),

    path("review-application/<int:application_id>/", review_application, name="review_application"),   
    
    path('allaid/', all_aid_list, name='all_aid_list'),
    
    path("propose_aid/", propose_aid_program, name="propose_aid"),
    path("my_proposals/", my_proposals, name="my_proposals"),
    path("review/", funder_review_applications, name="funder_review_applications"),
    path("approve/<int:application_id>/", funder_approve_application, name="funder_approve_application"),
    path("reject/<int:application_id>/", funder_reject_application, name="funder_reject_application"),

        
        
        
    path("review_aid_program/", review_aid_program, name="review_aid_program"),
    path("approve_aid/<int:aid_id>/", approve_aid, name="approve_aid"),
    path("reject_aid/<int:aid_id>/", reject_aid, name="reject_aid"),
    
    
    
    path('Sfund/', student_fund_utilization, name='student_fund_utilization'),
    path('Afund/', aid_officer_monitor_utilization, name='aid_officer_utilization'),
    path('flag/<int:utilization_id>/', flag_fund_utilization, name='flag_fund_utilization'),
    path('Ffund/', funder_view_utilization, name='funder_utilization'),
    path('acknowledge/<int:utilization_id>/', acknowledge_fund_utilization, name='acknowledge_fund_utilization'),
]
