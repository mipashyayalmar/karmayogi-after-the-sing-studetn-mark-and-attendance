from django.urls import path
from . import views

urlpatterns = [
    path('registration', views.employee_registration, name='employee-registration'),
    path('list', views.employee_list, name='employee-list'),
    path('load-upazilla', views.load_upazilla, name='load-upazilla'),
    path('profile/<employee_id>', views.employee_profile, name='employee_profile'),
    path('edit/<employee_id>', views.employee_edit, name='employee_edit'),
    path('delete/<employee_id>', views.employee_delete, name='employee_delete'),
    path('employee/send_message/<int:employee_id>/', views.send_message, name='send_message'),

    path('messages/<int:employee_id>/', views.employee_messages, name='employee_messages'),
    path('messages/', views.messages_list, name='messages_list'),  # Added this
]
