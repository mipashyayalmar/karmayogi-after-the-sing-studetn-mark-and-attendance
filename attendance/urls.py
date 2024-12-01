from django.urls import path
from .views import student_attendance, SetAttendance, add_attendance, add_marks, view_marks


urlpatterns = [
    path('student/', student_attendance, name='student-attendance'),
    path('set-attendance/<std_class>/<std_roll>/', SetAttendance.as_view(), name='set-attendance'),
    path('add-attendance/', add_attendance, name='add_attendance'),
    path('add-marks/', add_marks, name='add-marks'), 
    path('view-marks/', view_marks, name='view-marks'),
]
