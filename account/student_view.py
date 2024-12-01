from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from attendance.models import EnrolledStudent, StudentAttendance
from student.models import AcademicInfo
from academic.models import ClassRegistration, Session
from result.models import SubjectRegistration
from employee.models import PersonalInfo as EmployeePersonalInfo
from teacher.models import PersonalInfo as TeacherPersonalInfo
import json
from .models import Message

@login_required(login_url='login')
def student_profile(request, student_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Ensure the user is a student
    if user_profile.employee_type == 'student':
        # Retrieve the correct student profile
        if not student_id:
            student = get_object_or_404(AcademicInfo, userprofile=user_profile)
        else:
            student = get_object_or_404(AcademicInfo, id=student_id)

        # Verify the student profile matches the logged-in user's profile
        if student.userprofile == user_profile:
            try:
                # Get the enrolled student record
                enrolled_student = EnrolledStudent.objects.get(student=student)

                # Get class and session details
                student_class = user_profile.student_class
                student_session = user_profile.student_session

                # Filter subjects for the student's specific class and session
                subjects = SubjectRegistration.objects.filter(
                    select_class__class_name=student_class,
                    session_info=student_session
                )

                # Calculate attendance by subject
                subject_wise_attendance = {}
                for subject in subjects:
                    subject_records = StudentAttendance.objects.filter(student=enrolled_student, subject=subject)
                    present_count = subject_records.filter(status=1).count()
                    absent_count = subject_records.filter(status=0).count()
                    total_days = present_count + absent_count
                    percentage = (present_count / total_days * 100) if total_days > 0 else 0

                    subject_wise_attendance[subject.subject_name] = {
                        'present': present_count,
                        'absent': absent_count,
                        'total_days': total_days,
                        'percentage': round(percentage, 2)  # Rounded to 2 decimal places
                    }

                # Convert attendance data to JSON for graph generation in JavaScript
                subject_wise_attendance_json = json.dumps(subject_wise_attendance)

                # Filter teachers and employees in the same department
                student_department = user_profile.department
                teachers_in_same_department = TeacherPersonalInfo.objects.filter(job__department=student_department)
                teacher_count = teachers_in_same_department.count()
                employees_in_same_department = EmployeePersonalInfo.objects.filter(job__department=student_department)
                employee_count = employees_in_same_department.count()

                # Additional statistics
                total_student = AcademicInfo.objects.count()
                total_classes = ClassRegistration.objects.count()
                total_sessions = Session.objects.count()
                total_subjects = subjects.count()

                # Unread messages for the student
                messages = Message.objects.filter(recipient=request.user)
                unread_count = messages.filter(is_read=False).count()  # Count unread messages

                # Prepare context data for template rendering
                context = {
                    'student': student,
                    'profile': user_profile,
                    'total_student': total_student,
                    'total_classes': total_classes,
                    'total_sessions': total_sessions,
                    'subjects': subjects,
                    'total_subjects': total_subjects,
                    'teacher_count': teacher_count,
                    'employee_count': employee_count,
                    'teachers_in_same_department': teachers_in_same_department,
                    'employees_in_same_department': employees_in_same_department,
                    'subject_wise_attendance': subject_wise_attendance_json,  # JSON data for JS graph
                    'subject_attendance_percentages': subject_wise_attendance,  # Python data for HTML table
                    'unread_count': unread_count,  # Add unread message count to context
                }

                return render(request, 'student/home.html', context)

            except EnrolledStudent.DoesNotExist:
                # Redirect to a custom error page if the EnrolledStudent is not found
                return render(request, 'error/not_enroll.html')
        else:
            return render(request, 'error/not_enroll.html')
    else:
        return render(request, 'error/not_enroll.html')
