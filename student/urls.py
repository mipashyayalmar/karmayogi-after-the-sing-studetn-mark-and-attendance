from django.urls import path
from . import views
from .views import student_attendance, student_marks,student_undo_delete

urlpatterns = [
    path('class-wise-student-registration', views.class_wise_student_registration, name='class-wise-student-registration'),
    path('student-registration', views.student_registration, name='student-registration'),
    path('student-list', views.student_list, name='student-list'),
    path('profile/<reg_no>/', views.student_profile, name='student-profile'),  # Added trailing slash
    path('edit/<reg_no>/', views.student_edit, name='student-edit'),  # Added trailing slash
    path('delete/<reg_no>/', views.student_delete, name='student-delete'),  # Added trailing slash
    path('student-search/', views.student_search, name='student-search'),
    path('enrolled/', views.enrolled_student, name='enrolled-student'),
    path('student-enrolled/<reg>/', views.student_enrolled, name='student-enrolled'),  # Updated name and added trailing slash
    path('enrolled-student-list/', views.enrolled_student_list, name='enrolled-student-list'),
    path('inbox/', views.student_inbox, name='student-inbox'),
    path('message/<int:message_id>/', views.student_read_message, name='student-read-message'),

    path('undo-delete-student/<str:reg_no>/', student_undo_delete, name='student-undo-delete'),

    path('student/<int:student_id>/attendance/', student_attendance, name='student_attendance'),
    path('student/<int:student_id>/marks/', student_marks, name='student_marks'),

]
