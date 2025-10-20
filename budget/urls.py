from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('', views.home, name='home'),
    path('create/', views.create_budget, name='create_budget'),
    path('budget/<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('budget/<int:budget_id>/add_expense/', views.add_expense, name='add_expense'),
    path('budget/<int:budget_id>/add_income/', views.add_income, name='add_income'),
    path('budget/<int:budget_id>/edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('budget/<int:budget_id>/edit_income/<int:income_id>/', views.edit_income, name='edit_income'),
    path('budget/<int:budget_id>/delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('budget/<int:budget_id>/delete_income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('budget/<int:budget_id>/export_csv/', views.export_csv, name='export_csv'),
    
    # New Project Costing URLs
    path('project-costings/', views.project_costing_list, name='project_costing_list'),
    path('project-costings/create/', views.create_project_costing, name='create_project_costing'),
    path('project-costings/<int:pk>/', views.project_costing_detail, name='project_costing_detail'),
    path('project-costings/<int:pk>/edit/', views.edit_project_costing, name='edit_project_costing'),
    
    # Superuser Dashboard URLs
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('project-costings/<int:pk>/review/', views.review_project_costing, name='review_project_costing'),
    path('project-costings/<int:pk>/generate-quotation/', views.generate_quotation, name='generate_quotation'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
    
    # Enhanced Dashboard URLs
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('submit-project/', views.submit_project, name='submit_project'),
    path('project/<str:tracking_id>/', views.project_detail, name='project_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('review-project/<str:tracking_id>/', views.review_project, name='review_project'),
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('project-tracking/', views.project_tracking, name='project_tracking'),
]