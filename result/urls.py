from django.urls import path
from .views import add_subject, subject_list, subject_detail

urlpatterns = [
    path('add-subject', add_subject, name='add-subject'),
    path('subject-list', subject_list, name='subject-list'),
    path('subject/<int:pk>/', subject_detail, name='subject-detail'),  # Use subject_detail directly
]
