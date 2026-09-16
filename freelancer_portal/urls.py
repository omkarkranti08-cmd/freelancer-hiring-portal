from django.urls import path,include
from accounts import views

urlpatterns = [
    path('__reload__/', include('django_browser_reload.urls')),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards & Jobs
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/freelancer/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('jobs/', views.browse_jobs, name='browse_jobs'),
    path('jobs/create/', views.create_job_view, name='create_job'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_to_job, name='apply_job'),
    
    # Contract Management
    path('proposal/<int:application_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposal/<int:application_id>/reject/', views.reject_proposal, name='reject_proposal'),
    path('job/<int:job_id>/submit/', views.submit_project_work, name='submit_project_work'),
    path('job/<int:job_id>/approve/', views.approve_and_payout, name='approve_and_payout'),

    # Profile & Workspace
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('workspace/<int:project_id>/', views.project_workspace_view, name='project_workspace'),

     # urls.py — add these two
    path('job/<int:job_id>/messages/', views.chat_thread_view, name='chat_thread'),
    path('inbox/', views.inbox_view, name='inbox'),
]