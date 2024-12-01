from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import UserProfile
from .forms import SearchEnrolledStudentForm, AttendanceForm
from student.models import EnrolledStudent
from academic.models import ClassRegistration, Session
from .models import StudentAttendance, AttendanceManager
from django.contrib import messages  
from django.urls import reverse
from django.db.models import Q
from .forms import SearchEnrolledStudentForm, MarkForm
from .models import StudentMark, EnrolledStudent
from result.models import SubjectRegistration
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from student.forms import StudentProfileUpdateForm
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from teacher.models import  PersonalInfo as TeacherPersonalInfo
from django.http import HttpResponseForbidden



@login_required(login_url='login')
def student_attendance(request, teacher_id=None):
    # Get or create the user's profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'employee_type': 'professor'})

    # Redirect if the user is not authorized
    if user_profile.employee_type not in ['professor', 'teacher', 'student']:
        return redirect('login')

    # Fetch teacher profile if user is a teacher or professor
    teacher = None
    if user_profile.employee_type in ['teacher', 'professor']:
        if teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    # Set the default search query to the user's profile name if no search is provided
    search_query = request.GET.get('search', '')
    if user_profile.employee_type == 'student' and not search_query:
        search_query = user_profile.name  # Use the UserProfile name as the default search query

    # Initialize search form and filters
    forms = SearchEnrolledStudentForm(request.GET or None, user_profile=user_profile)
    class_name = request.GET.get('reg_class')
    session_year = request.GET.get('session')
    attendance_date = request.GET.get('attendance_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    subject_id = request.GET.get('subject')

    # Fetch all attendance records initially
    attendances = StudentAttendance.objects.all().order_by('-date', '-timestamp')
    subjects = []

    # Specific filtering for students
    if user_profile.employee_type == 'student':
        student_class = user_profile.student_class
        student_session = user_profile.student_session

        # Filter attendance by student’s class and session
        if student_class and student_session:
            class_info = get_object_or_404(ClassRegistration, class_name=student_class, session=student_session)
            attendances = attendances.filter(select_class=class_info)
            subjects = SubjectRegistration.objects.filter(select_class=class_info)

    # Apply filters based on search query and other parameters
    if search_query:
        attendances = attendances.filter(
            Q(student__student__userprofile__name__icontains=search_query) |
            Q(student__student__registration_no__icontains=search_query) |
            Q(subject__subject_name__icontains=search_query)
        )

    # Additional filters for attendance based on class, session, and date
    if class_name and session_year:
        try:
            class_info = ClassRegistration.objects.get(id=class_name, session_id=session_year)
            attendances = attendances.filter(select_class=class_info)
            subjects = SubjectRegistration.objects.filter(select_class=class_info)
        except ClassRegistration.DoesNotExist:
            attendances = StudentAttendance.objects.none()

    if attendance_date:
        attendances = attendances.filter(date=attendance_date)

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            attendances = attendances.filter(date__range=(start_date, end_date))
        except ValueError:
            pass

    if subject_id:
        attendances = attendances.filter(subject__id=subject_id)

    # Calculate subject-wise attendance counts
    subject_attendance_counts = defaultdict(lambda: {'present': 0, 'absent': 0})
    for attendance in attendances:
        status = attendance.get_status_display().lower()  # 'present' or 'absent'
        subject_attendance_counts[attendance.subject.subject_name][status] += 1

    # Calculate attendance percentage and average attendance for each subject
    subject_attendance_percentages = {}
    for subject, counts in subject_attendance_counts.items():
        total_days = counts['present'] + counts['absent']
        if total_days > 0:
            percentage = (counts['present'] / total_days) * 100
            subject_attendance_percentages[subject] = {
                'percentage': round(percentage, 2),
                'present': counts['present'],
                'absent': counts['absent'],
                'total_days': total_days
            }

    # Convert defaultdict to a regular dictionary before passing to the template
    subject_attendance_counts = dict(subject_attendance_counts)

    context = {
        'profile': user_profile,
        'teacher': teacher,  # Include teacher profile in context
        'teacher_id': teacher.id if teacher else None,  # Pass teacher ID to the template if available
        'forms': forms,
        'attendances': attendances,
        'search_query': search_query,
        'subjects': subjects,
        'employee_type': user_profile.employee_type,
        'subject_attendance_counts': json.dumps(subject_attendance_counts),  # JSON format
        'subject_attendance_percentages': subject_attendance_percentages,  # Add percentages
    }

    return render(request, 'attendance/student-attendance.html', context)

class SetAttendance(APIView):
    def get(self, request, std_class, std_roll):
        try:
            StudentAttendance.objects.create_attendance(std_class, std_roll)
            return Response({'status': 'Success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'Failed', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            


@login_required(login_url='login')
def add_attendance(request, teacher_id=None):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'employee_type': 'professor'})

    # Ensure the user has the correct permissions
    if user_profile.employee_type not in ['professor', 'teacher']:
        return redirect('login')

    # Fetch the teacher profile based on the teacher_id or the logged-in user's profile
    if user_profile.employee_type in ['teacher', 'professor']:
        if teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)
    else:
        return redirect('login')

    # Get selected class, session, and subject from the request parameters
    class_id = request.GET.get('class_id')
    session_year = request.GET.get('session_year')
    subject_id = request.GET.get('subject')

    # Fetch selected class and session if provided
    selected_class = ClassRegistration.objects.filter(id=class_id).first()
    selected_session = Session.objects.filter(id=session_year).first()

    students, subjects = [], []
    if selected_class and selected_session:
        # Get students enrolled in the selected class and session
        students = EnrolledStudent.objects.filter(class_name=selected_class, session_year=selected_session)
        
        # Get subjects based on fields that exist in SubjectRegistration
        subjects = SubjectRegistration.objects.filter(select_class=selected_class, session_info=selected_session)

    # Initialize the attendance form with subject and request data
    form = AttendanceForm(request.POST or None, class_id=class_id, session_year=session_year, initial={'subject': subject_id})

    if request.method == "POST" and form.is_valid():
        subject = form.cleaned_data.get('subject')
        attendance_date = form.cleaned_data.get('attendance_date')
        selected_student_ids = request.POST.getlist('student_ids')
        attendance_saved = False

        for roll in selected_student_ids:
            student = EnrolledStudent.objects.filter(class_name=selected_class, roll=roll, session_year=selected_session).first()
            if student and subject and attendance_date:
                attendance_status = request.POST.get(f'attendance_status_{roll}', '0')
                if attendance_status is not None:
                    try:
                        AttendanceManager().create_attendance(
                            std_class=selected_class.name,
                            std_roll=student.roll,
                            subject=subject,
                            attendance_date=attendance_date,
                            status=int(attendance_status)
                        )
                        attendance_saved = True
                    except Exception as e:
                        messages.error(request, f"Failed to submit attendance for roll {roll}: {str(e)}")

        if attendance_saved:
            messages.success(request, "Attendance added successfully!")
            return redirect(reverse('add_attendance') + f'?class_id={class_id}&session_year={session_year}&subject={subject_id}')
        else:
            messages.error(request, "Failed to submit attendance. Please check your entries.")

    # Prepare context including the teacher's profile
    context = {
        'form': form,
        'profile': user_profile,
        'teacher': teacher,  # Pass teacher's profile to the template
        'teacher_id': teacher.id,  # Pass teacher's ID to the template
        'selected_class': selected_class,
        'selected_session': selected_session,
        'students': students,
        'subjects': subjects,
        'classes': ClassRegistration.objects.all(),
        'sessions': Session.objects.all(),
    }
    return render(request, 'attendance/add_attendance.html', context)

@login_required(login_url='login')
def view_marks(request, teacher_id=None):
    # Initialize the filter form
    filter_form = SearchEnrolledStudentForm(request.GET or None)
    marks_query = StudentMark.objects.none()  # Start with an empty QuerySet
    subjects = SubjectRegistration.objects.none()  # Ensure subjects is initialized
    search_query = request.GET.get('search', '')  # Get the search query if present

    # Get the logged-in user's profile
    user_profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={'employee_type': 'professor'}
    )

    # Ensure only teachers or professors can access this view
    if user_profile.employee_type not in ['professor', 'teacher']:
        return redirect('login')

    # Fetch the teacher's profile based on the teacher_id or the logged-in user's profile
    teacher = None
    if teacher_id:
        teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
    else:
        teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    # Ensure the teacher matches the logged-in user's profile
    if teacher.address.userprofile != user_profile:
        return redirect('login')

    # Process the filter form
    if filter_form.is_valid():
        reg_class = filter_form.cleaned_data.get('reg_class')
        session = filter_form.cleaned_data.get('session')
        subject = filter_form.cleaned_data.get('subject')
        mark_type = filter_form.cleaned_data.get('mark_type')

        # Filter subjects based on the selected class and session
        if reg_class and session:
            subjects = SubjectRegistration.objects.filter(
                select_class=reg_class, session_info=session
            ).distinct()

        # Build filter criteria for marks
        filter_criteria = {}
        if reg_class:
            filter_criteria['student__class_name'] = reg_class
        if session:
            filter_criteria['student__session_year'] = session
        if subject:
            filter_criteria['subject'] = subject
        if mark_type:
            filter_criteria['mark_type__icontains'] = mark_type  # Allows partial matches

        # Fetch the filtered student marks
        if filter_criteria:
            marks_query = StudentMark.objects.filter(**filter_criteria).distinct()

        # Implement search functionality
        if search_query:
            marks_query = marks_query.filter(
                Q(student__student__personal_info__name__icontains=search_query) |
                Q(subject__subject_name__icontains=search_query)
            )

    # Prepare context for rendering
    context = {
        'filter_form': filter_form,
        'marks_data': marks_query,
        'subjects': subjects,
        'profile': user_profile,
        'search_query': search_query,
        'teacher': teacher,  # Include teacher information in the context
        'teacher_id': teacher.id if teacher else None,  # Pass teacher ID to the template
    }

    return render(request, 'attendance/view_marks.html', context)







def add_marks(request, teacher_id=None):
    filter_form = SearchEnrolledStudentForm(request.GET or None)
    students = EnrolledStudent.objects.none()
    student_form_pairs = []
    subjects = SubjectRegistration.objects.none()
    search_query = request.GET.get('search', '')
    mark_type_filter = request.GET.get('mark_type', '')  

    
    user_profile = get_object_or_404(UserProfile, user=request.user)

    
    if user_profile.employee_type in ['teacher', 'professor']:
        if teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")

    
    teacher_id = teacher.id 

    reg_class = None
    session = None

    # Filter students based on the form inputs
    if filter_form.is_valid():
        reg_class = filter_form.cleaned_data.get('reg_class')
        session = filter_form.cleaned_data.get('session')
        filter_criteria = {}

        if reg_class:
            filter_criteria['class_name'] = reg_class
        if session:
            filter_criteria['session_year'] = session.id 

        if filter_criteria:
            students = EnrolledStudent.objects.filter(**filter_criteria).distinct()

            if search_query:
                students = students.filter(
                    Q(student__personal_info__name__icontains=search_query) |
                    Q(roll__icontains=search_query)
                )
            if mark_type_filter:
                students = students.filter(studentmark__mark_type=mark_type_filter)

            student_form_pairs = [
                (student, MarkForm(prefix=f"mark_form_{student.id}", class_id=reg_class.id if reg_class else None, session_year=session.id if session else None))
                for student in students
            ]

            if reg_class and session:
                subjects = SubjectRegistration.objects.filter(select_class=reg_class, session_info=session.id).distinct()

    # Automatically select all students by default if no filters are applied
    if not students.exists() and reg_class and session:
        students = EnrolledStudent.objects.filter(class_name=reg_class, session_year=session)

        student_form_pairs = [
            (student, MarkForm(prefix=f"mark_form_{student.id}", class_id=reg_class.id if reg_class else None, session_year=session.id if session else None))
            for student in students
        ]

    # Handle POST request to save marks
    if request.method == 'POST':
        # Extract shared inputs
        subject_id = request.POST.get('subject')
        exam_date = request.POST.get('exam_date')
        mark_type = request.POST.get('mark_type')
        total_score = request.POST .get('total_score')

        # Validate shared inputs
        if not subject_id or not exam_date or not mark_type:
            messages.error(request, "Subject, exam date, and mark type are required.")
            return redirect('add-marks')

        subject = get_object_or_404(SubjectRegistration, id=subject_id)

        # Save marks for each student
        for student, form in student_form_pairs:
            score = request.POST.get(f'score_{student.id}')
            if score:
                try:
                    StudentMark.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_date=exam_date,
                        mark_type=mark_type,
                        total_score=total_score,
                        defaults={'score': score}
                    )
                    messages.success(request, f"Marks updated for {student.student.personal_info.name} (Roll: {student.roll}).")
                except Exception as e:
                    messages.error(request, f"Error saving marks for {student.student.personal_info.name}: {str(e)}")

        return redirect('add-marks')

    # Prepare context, including the teacher ID and mark type filter
    context = {
        'filter_form': filter_form,
        'student_form_pairs': student_form_pairs,
        'subjects': subjects,
        'profile': user_profile,
        'teacher': teacher,  # Pass the teacher's profile to the template
        'teacher_id': teacher_id,  # Pass the teacher's ID to the template
        'search_query': search_query,  # Pass search query to template
        'mark_type_filter': mark_type_filter,  # Pass the mark_type filter to the template
    }
    return render(request, 'attendance/add-marks.html', context)

