from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import UserProfile
from student.models import AcademicInfo
from teacher.models import PersonalInfo as TeacherPersonalInfo
from employee.models import PersonalInfo as EmployeePersonalInfo
from academic.models import ClassRegistration
from result.models import SubjectRegistration  
from account.models import Message  # Import the Message model

@login_required(login_url='login')
def teacher_profile(request, teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.employee_type in ['teacher', 'professor']:
        if not teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)

        if teacher.address.userprofile == user_profile or user_profile.employee_type == 'professor':
            all_teachers = TeacherPersonalInfo.objects.all()
            total_student = AcademicInfo.objects.count()
            total_teacher = TeacherPersonalInfo.objects.count()
            total_employee = EmployeePersonalInfo.objects.count()
            total_class = ClassRegistration.objects.count()
            total_subjects = SubjectRegistration.objects.all()  # Get all subjects
            
            # Count unread messages for the teacher
            unread_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()

            context = {
                'teacher': teacher,
                'profile': user_profile,
                'all_teachers': all_teachers,
                'student': total_student,
                'teacher_count': total_teacher,
                'employee': total_employee,
                'total_class': total_class,
                'total_subjects': total_subjects,  # Add total subjects to context
                'unread_messages_count': unread_messages_count,  # Include unread messages count
            }
            return render(request, 'teacher/home.html', context)
        else:
            return HttpResponseForbidden("You do not have permission to view this profile.")
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")

@login_required(login_url='login')
def professor_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.employee_type != 'professor':
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Fetch all subjects for the professor
    all_subjects = SubjectRegistration.objects.all()  # Get all subjects

    total_student = AcademicInfo.objects.count()
    total_teacher = TeacherPersonalInfo.objects.count()
    total_employee = EmployeePersonalInfo.objects.count()
    total_class = ClassRegistration.objects.count()
    total_subjects = SubjectRegistration.objects.all()  # Get all subjects
    
    # Count unread messages for the professor
    unread_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'student': total_student,
        'teacher': total_teacher,
        'employee': total_employee,
        'total_class': total_class,
        'profile': user_profile,
        'all_subjects': all_subjects, 
        'unread_messages_count': unread_messages_count,  
    }

    return render(request, 'professor/home.html', context)
