from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from collections import defaultdict
from .models import UserProfile
from student.models import AcademicInfo
from teacher.models import PersonalInfo as TeacherPersonalInfo
from employee.models import PersonalInfo as EmployeePersonalInfo
from academic.models import ClassRegistration
from attendance.models import StudentAttendance
from result.models import SubjectRegistration
from account.models import Message

@login_required(login_url='login')
def teacher_profile(request, teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Ensure the user has the correct permissions
    if user_profile.employee_type not in ['teacher', 'professor', 'principal']:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Get the teacher's profile, whether the logged-in user or a specific teacher ID
    teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id) if teacher_id else get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    if teacher.address.userprofile != user_profile and user_profile.employee_type not in ['professor', 'principal']:
        return HttpResponseForbidden("You do not have permission to view this profile.")

    # Gather data for dashboard stats
    all_teachers = TeacherPersonalInfo.objects.all()
    total_student = AcademicInfo.objects.count()
    total_teacher = all_teachers.count()
    total_employee = EmployeePersonalInfo.objects.count()
    total_class = ClassRegistration.objects.count()

    # Fetch subjects assigned to this teacher
    assigned_subjects = SubjectRegistration.objects.filter(userprofile=teacher.address.userprofile)

    # Calculate attendance for each subject
    subject_attendance_percentages = {}
    for subject in assigned_subjects:
        attendances = StudentAttendance.objects.filter(subject=subject)
        present_count = attendances.filter(status=1).count()
        absent_count = attendances.filter(status=0).count()
        total_days = present_count + absent_count
        percentage = (present_count / total_days * 100) if total_days > 0 else 0

        subject_attendance_percentages[subject.subject_name] = {
            'present': present_count,
            'absent': absent_count,
            'total_days': total_days,
            'percentage': round(percentage, 2)
        }

    # Fetch unread messages count for the teacher
    unread_messages_count = 0
    if user_profile.employee_type == 'teacher':
        unread_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    # Render context for template
    context = {
        'teacher': teacher,
        'profile': user_profile,
        'all_teachers': all_teachers,
        'student': total_student,
        'teacher_count': total_teacher,
        'employee': total_employee,
        'total_class': total_class,
        'total_subjects': assigned_subjects,
        'subject_count': assigned_subjects.count(),
        'subject_attendance_percentages': subject_attendance_percentages,
        'unread_messages_count': unread_messages_count,  # Add unread messages count to context
    }

    return render(request, 'teacher/home.html', context)
