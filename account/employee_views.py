from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import UserProfile
from employee.models import PersonalInfo as EmployeePersonalInfo
from teacher.models import PersonalInfo as TeacherPersonalInfo
from employee.models import EmployeeMessage  # Import the EmployeeMessage model

@login_required(login_url='login')
def employee_profile(request, employee_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Ensure the user is an employee
    if user_profile.employee_type == 'employee':
        # Retrieve the correct employee profile
        if not employee_id:
            employee = get_object_or_404(EmployeePersonalInfo, userprofile=user_profile)
        else:
            employee = get_object_or_404(EmployeePersonalInfo, id=employee_id)

        # Verify the employee profile matches the logged-in user's profile
        if employee.userprofile == user_profile:
            # Get department details
            employee_department = employee.job.department if employee.job and employee.job.department else None

            if not employee_department:
                return HttpResponseForbidden("This employee does not belong to a department or has incomplete information.")

            # Filter employees and teachers in the same department
            employees_in_same_department = EmployeePersonalInfo.objects.filter(job__department=employee_department)
            employee_count = employees_in_same_department.count()

            teachers_in_same_department = TeacherPersonalInfo.objects.filter(job__department=employee_department)
            teacher_count = teachers_in_same_department.count()

            # Additional statistics
            total_employees = EmployeePersonalInfo.objects.count()
            total_teachers = TeacherPersonalInfo.objects.count()

            # Count total messages for the employee
            total_messages = EmployeeMessage.objects.filter(employee=employee).count()

            # Count unread messages
            total_unread_messages = EmployeeMessage.objects.filter(employee=employee, is_read=False).count()

            # Prepare context data for template rendering
            context = {
                'employee': employee,
                'profile': user_profile,
                'department': employee_department,
                'total_employees': total_employees,
                'total_teachers': total_teachers,
                'employee_count': employee_count,
                'teacher_count': teacher_count,
                'employees_in_same_department': employees_in_same_department,
                'teachers_in_same_department': teachers_in_same_department,
                'total_messages': total_messages,  # Total messages count
                'total_unread_messages': total_unread_messages,  # Unread messages count
            }

            return render(request, 'employee/home.html', context)
        else:
            return HttpResponseForbidden("You do not have permission to view this profile.")
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")
