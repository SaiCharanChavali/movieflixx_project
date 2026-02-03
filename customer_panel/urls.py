from django.urls import path
from customer_panel import views

urlpatterns = [

    # Auth
    path('customer_register_page/', views.customer_register_page, name='customer_register'),
    path('customer_login_page/', views.customer_login_page, name='customer_login'),

    path('forgot_password/', views.forgot_password),
    path('reset_password/', views.reset_password),


    # Dashboard & Profile
    path('customer_dashboard_page/', views.customer_dashboard_page, name='customer_dashboard'),
    path('customer_update_profile/', views.customer_update_profile, name='update_profile'),
    path('customer_profile_settings_page/', views.customer_profile_settings_page, name='customer_profile_settings'),
    path('Customerchange_password/', views.Customerchange_password, name='Customerchange_password'),

    # Movies & Series
    path('customer_movie_page/', views.customer_movie_page, name='customer_movie'),
    path('movie/<int:movie_id>/', views.customer_movie_detail, name='customer_movie_detail'),

    path('customer_web_series_page/', views.customer_web_series_page, name='customer_web_series'),

    # AJAX
    path('get_episodes_for_customer/', views.get_episodes_for_edit, name='get_episodes_for_customer'),

    # Players (⚠️ fixed name)
    path('movie_details/<int:movie_id>/', views.Video_player_view, name='video_player_view'),
    path('web_series_player/<int:series_id>/', views.web_series_player_view, name='web_series_player'),

    # Subscription
    path('subscription_plans/', views.subscription_plans_page, name='subscription_plans'),
    path('process-subscription/<int:plan_id>/<str:c_type>/<int:c_id>/', 
     views.process_subscription, name='process_subscription'), 
    # Add these for the Razorpay flow
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    # path('payment-callback/', views.payment_callback, name='payment_callback'),
    # path('payment-failed/', views.payment_failed, name='payment_failed'),
 
 path('process-subscription/<int:plan_id>/', views.process_subscription, name='process_subscription'),
    path('toggle_notifications/', views.toggle_notifications, name='toggle_notifications'),
]
