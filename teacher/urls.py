from django.urls import path

from . import views

urlpatterns = [
    path('registration', views.teacher_registration, name='teacher-registration'),
    path('list', views.teacher_list, name='teacher-list'),
    path('profile/<int:teacher_id>', views.teacher_profile, name='teacher-profile'),
    path('delete/<int:teacher_id>/', views.teacher_delete, name='teacher-delete'),
    path('edit/<teacher_id>', views.teacher_edit, name='teacher-edit'),
    path('load-upazilla', views.load_upazilla, name='load-upazilla'),
    path('teacher/send_message/<int:teacher_id>/', views.send_message, name='send-message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<int:message_id>/', views.read_message, name='read-message'),

]
