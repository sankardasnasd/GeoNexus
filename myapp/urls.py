from django.contrib import admin
from django.urls import path

from myapp import views

urlpatterns = [
    path('logout/', views.fun_logout),
    path('login/', views.login_get),
    path('login_post/', views.login_post),
    path('camp_coordinator_home/', views.camp_coordinator_home),
    path('admin_home/', views.admin_home),
    path('registration/', views.registration),
    path('registration_post/', views.registration_post),
    path('camp_coordinator_viewprofile/', views.camp_coordinator_viewprofile),
    path('camp_coordinator_editprofile/', views.camp_coordinator_editprofile),
    path('camp_coordinator_editprofile_post/', views.camp_coordinator_editprofile_post),
    path('admin_view_feedback/', views.admin_view_feedback),
    path('admin_view_complaints/', views.admin_view_complaints),
    path('send_reply/<id>/', views.send_reply),
    path('send_reply_post/', views.send_reply_post),

    path('admin_assign_volunteer/<id>/', views.admin_assign_volunteer),
    path('admin_assign_volunteer_post/', views.admin_assign_volunteer_post),
    path('admin_verify_volunteers/', views.verify_volunteers),
    path('approve_volunteers/<id>/', views.approve_volunteers),
    path('reject_volunteers/<id>/', views.reject_volunteers),
    path(
        'admin_view_assigned_volunteers/',
        views.admin_view_assigned_volunteers,
        name='admin_view_assigned_volunteers'
    ),

    path(
        'admin_delete_assigned_volunteer/<int:id>/',
        views.admin_delete_assigned_volunteer,
        name='admin_delete_assigned_volunteer'
    ),

    path('add_requirements/<id>/', views.add_requirements),
    path('add_requirements_post/', views.add_requirements_post),
    path('view_requirements/', views.view_requirements),
    path('edit_requirement/<id>/', views.edit_requirement),
    path('edit_requirement_post/', views.edit_requirement_post),
    path('delete_requirement/<id>/', views.delete_requirement),

    path('add_inventory/<id>/', views.add_inventory),
    path('add_inventory_post/', views.add_inventory_post),
    path('view_inventory/', views.view_inventory),
    path('edit_inventory/<id>/', views.edit_inventory),
    path('edit_inventory_post/', views.edit_inventory_post),
    path('delete_inventory/<id>/', views.delete_inventory),
    path('coordinator_view_ert/', views.coordinator_view_ert),
    path('coordinator_view_volunteers/', views.coordinator_view_volunteers),

    path('view_goods_donations/', views.view_goods_donations),
    path('coordinator_assigntask_volunteer/<id>/', views.coordinator_assigntask_volunteer),
    path('admin_assigntask_volunteer_post/', views.admin_assigntask_volunteer_post),

    path('chat/<id>', views.chat1),
    path('chat_view/', views.chat_view),
    path('chat_send/<msg>', views.chat_send),

    path('User_sendchat/', views.User_sendchat),
    path('User_viewchat/', views.User_viewchat),

    path('chat2/<id>', views.chat2),
    path('chat_view2/', views.chat_view2),
    path('chat_send2/<msg>', views.chat_send2),

    path(
        'manage_disaster_victim/',
        views.manage_disaster_victim,
        name='manage_disaster_victim'
    ),

    path(
        'add_disaster_victim/',
        views.add_disaster_victim,
        name='add_disaster_victim'
    ),

    path(
        'add_disaster_victim_post/',
        views.add_disaster_victim_post,
        name='add_disaster_victim_post'
    ),

    path(
        'edit_disaster_victim/<int:id>/',
        views.edit_disaster_victim,
        name='edit_disaster_victim'
    ),

    path(
        'edit_disaster_victim_post/<int:id>/',
        views.edit_disaster_victim_post,
        name='edit_disaster_victim_post'
    ),

    path(
        'delete_disaster_victim/<int:id>/',
        views.delete_disaster_victim,
        name='delete_disaster_victim'
    ),

    path('admin_add_ert/', views.admin_add_ert, name='admin_add_ert'),
    path('admin_add_ert_post/', views.admin_add_ert_post, name='admin_add_ert_post'),
    path('admin_view_ert/', views.admin_view_ert, name='admin_view_ert'),
    path('admin_ert_edit_post/', views.admin_ert_edit_post, name='admin_ert_edit_post'),
    path('admin_edit_ert/<id>', views.admin_edit_ert, name='admin_edit_ert'),
    path('admin_delete_ert/<id>', views.admin_delete_ert, name='admin_delete_ert'),

    path(
        'verify_camp_coordinator/',
        views.verify_camp_coordinator,
        name='verify_camp_coordinator'
    ),

    path(
        'approve_camp_coordinator/<int:id>/',
        views.approve_camp_coordinator,
        name='approve_camp_coordinator'
    ),

    path(
        'reject_camp_coordinator/<int:id>/',
        views.reject_camp_coordinator,
        name='reject_camp_coordinator'
    ),

    path(
        'manage_relief_camp/',
        views.manage_relief_camp,
        name='manage_relief_camp'
    ),

    path(
        'add_relief_camp/',
        views.add_relief_camp,
        name='add_relief_camp'
    ),

    path(
        'add_relief_camp_post/',
        views.add_relief_camp_post,
        name='add_relief_camp_post'
    ),
    path(
        'edit_relief_camp/<int:id>/',
        views.edit_relief_camp,
        name='edit_relief_camp'
    ),

    path(
        'edit_relief_camp_post/<int:id>/',
        views.edit_relief_camp_post,
        name='edit_relief_camp_post'
    ),
    path(
        'delete_camp/<int:id>/',
        views.delete_camp,
        name='delete_camp'
    ),

    path(
        'admin_view_preparedness_guidelines/',
        views.admin_view_preparedness_guidelines,
        name='admin_view_preparedness_guidelines'
    ),

    path(
        'admin_add_preparedness_guideline/',
        views.admin_add_preparedness_guideline,
        name='admin_add_preparedness_guideline'
    ),

    path(
        'admin_add_preparedness_guideline_post/',
        views.admin_add_preparedness_guideline_post,
        name='admin_add_preparedness_guideline_post'
    ),

    path(
        'admin_edit_preparedness_guideline/<int:id>/',
        views.admin_edit_preparedness_guideline,
        name='admin_edit_preparedness_guideline'
    ),

    path(
        'admin_edit_preparedness_guideline_post/',
        views.admin_edit_preparedness_guideline_post,
        name='admin_edit_preparedness_guideline_post'
    ),

    path(
        'admin_delete_preparedness_guideline/<int:id>/',
        views.admin_delete_preparedness_guideline,
        name='admin_delete_preparedness_guideline'
    ),

    path(
        'admin_view_notifications/',
        views.admin_view_notifications,
        name='admin_view_notifications'
    ),

    path(
        'admin_add_notification/',
        views.admin_add_notification,
        name='admin_add_notification'
    ),

    path(
        'admin_add_notification_post/',
        views.admin_add_notification_post,
        name='admin_add_notification_post'
    ),

    path(
        'admin_edit_notification/<int:id>/',
        views.admin_edit_notification,
        name='admin_edit_notification'
    ),

    path(
        'admin_edit_notification_post/',
        views.admin_edit_notification_post,
        name='admin_edit_notification_post'
    ),

    path(
        'admin_delete_notification/<int:id>/',
        views.admin_delete_notification,
        name='admin_delete_notification'
    ),

    path('change_password/', views.change_passwords),
    path('change_passwordposts/', views.change_passwordposts),

    path('view_emergency_alerts/', views.view_emergency_alerts),

    path('user_register/', views.user_register),
    path('volunteer_register/', views.volunteer_register),
    path('app_login/', views.app_login),
    path('user_viewprofile/', views.user_viewprofile),
    path('user_edit_profile/', views.user_edit_profile),
    path('app_changepassword/', views.app_changepassword),
    path('usersendcomplaint/', views.usersendcomplaint),
    path('userviewreply/', views.userviewreply),
    path('user_send_feedback/', views.usersendfeedback),
    path('userviewnearbycamp/', views.userviewnearbycamp),
    path('updatelocation/', views._update_location),
    path('userviewnotification/', views.userviewnotification),
    path('userguidelines/', views.userguidelines),
    path('userviewinventory/', views.userviewinventory),
    path('userviewrequirements/', views.userviewrequirements),
    path('donate_relief_goods/', views.donate_relief_goods),
    path('volunteer_viewprofile/', views.volunteer_viewprofile),
    path('volunteer_edit_profile/', views.volunteer_edit_profile),
    path('ert_viewprofile/', views.ert_viewprofile),
    path('volunteer_view_assigned_camp/', views.volunteer_view_assigned_camp),

    path('add_donation_bc_post/', views.add_donation_bc_post),
    path('user_view_send_donations/', views.user_view_send_donations),
    path('view_amount_requirement_donations/', views.view_amount_requirement_donations),

    path('user_view_goods_history/', views.user_view_goods_history),
    path('volunteer_view_assign_task/', views.volunteer_view_assign_task),
    path('update_assign_task/', views.update_assign_task),
    path('volunteerviewrequirements/', views.volunteerviewrequirements),
    path('volunteer_add_daily_report/', views.volunteer_add_daily_report),
    path('volunteerviewdailyreport/', views.volunteerviewdailyreport),
    path('delete_daily_report/', views.delete_daily_report),
    path('volunteerviewert/', views.volunteerviewert),
    path('ertviewcampcoordinator/', views.ertviewcampcoordinator),

    path('user_view_disaster_noti/', views.user_view_disaster_noti),
    path('nearby_alerts/', views.nearby_alerts),
    path('ert_view_disaster_predictions/', views.ert_view_disaster_predictions),
    path('user_view_disaster_notification/', views.user_view_disaster_notification),

    path('ertviewvolunteer/', views.ertviewvolunteer),
    path('ertviewvictim/', views.ertviewvictim),
    path('coordinator_view_daily_report/<id>', views.coordinator_view_daily_report),
    path('camp_coordinator_view_blockchain/', views.camp_coordinator_view_blockchain),
    path('admin_coordinator_view_blockchain/', views.admin_coordinator_view_blockchain),
    path('coordinator_generate_camp_report/<id>', views.coordinator_generate_camp_report),

    path(
        'admin_view_goods_distribution/',
        views.admin_view_goods_distribution,
        name='admin_view_goods_distribution'
    ),

    path(
        'webmap_start/',
        views.map_start,
        name='map_start'
    ),

    path(
        'webget_predict/',
        views.get_predict,
        name='webget_predict'
    ),

    path(
        "dummy_disaster_prediction/",
        views.dummy_disaster_prediction,
        name="dummy_disaster_prediction"
    ),

    #  path(
    #     'webmap_start/',
    #     views.webmap_start,
    #     name='webmap_start'
    # ),

    # path(
    #     'webget_predict/',
    #     views.webget_predict,
    #     name='webget_predict'
    # ),

    # path(
    #     'map_start/',
    #     views.map_start,
    #     name='map_start'
    # ),

    # path(
    #     'get_predict/',
    #     views.get_prediction,
    #     name='get_prediction'
    # ),

    # path('webmap_start/',views.webmap_start),

    path('emergency_sos/', views.emergency_sos),

    path('admin_emergency_requests/',views.view_emergency_sos,name='view_emergency_sos'),

    path('ert_view_emergency_noti/',views.ert_view_emergency_noti,name='ert_view_emergency_noti'),

    path("ert_nearby_emergencies/",views.ert_nearby_emergencies,name="ert_nearby_emergencies"),

    path('admin_view_ai_predictions/',views.admin_view_ai_predictions,name='admin_view_ai_predictions'),

    path('view_contacts/',views.view_contacts,name='view_contacts'),

    path('user_send_alert/',views.user_send_alert,name='user_send_alert'),
    path('forgotpasswordflutter/', views.forgotpasswordflutter),
    path('verifyOtpflutterPost/', views.verifyOtpflutterPost),
    path('changePasswodflutter/', views.changePasswordflutter),
    path('forgot_web/', views.forgot_web),
    path('forgotPassword_otp/', views.forgotPassword_otp),
    path('verifyOtp/', views.verifyOtp),
    path('verifyOtpPost/', views.verifyOtpPost),
    path('new_password/', views.new_password),
    path('changePassword/', views.changePassword),

    path('update_user_location/', views.update_user_location),
    path('update_user_location_for_landslide_prediction/', views.update_user_location_for_landslide_prediction),



]
