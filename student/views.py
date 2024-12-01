from academic.models import ClassRegistration
from account.models import UserProfile
from .forms import *
from .models import *
from django.db.models import Q
from .forms import StudentSearchForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AcademicInfo
import logging
from teacher.models import PersonalInfo as TeacherPersonalInfo
from django.urls import reverse

def load_upazilla(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor','teacher'])

    # if user_profile.employee_type != 'professor':
    #     return redirect('login')
    district_id = request.GET.get('district')
    upazilla = Upazilla.objects.filter(district_id=district_id).order_by('name')

    upazilla_id = request.GET.get('upazilla')
    union = Union.objects.filter(upazilla_id=upazilla_id).order_by('name')
    context = {
        'profile' : user_profile,
        'upazilla': upazilla,
        'union': union
    }
    return render(request, 'others/upazilla_dropdown_list_options.html', context)


def class_wise_student_registration(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor','teacher'])

    # if user_profile.employee_type != 'professor':
    #     return redirect('login')
    register_class = ClassRegistration.objects.all()
    context = {
        'register_class': register_class,
        'profile' : user_profile,
        }
    return render(request, 'student/class-wise-student-registration.html', context)




def student_registration(request, teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    teacher = None

    if user_profile.employee_type in ['teacher', 'professor']:
        if teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    # Initialize forms
    academic_info_form = AcademicInfoForm(request.POST or None)
    personal_info_form = PersonalInfoForm(request.POST or None, request.FILES or None)
    student_address_info_form = StudentAddressInfoForm(request.POST or None)
    guardian_info_form = GuardianInfoForm(request.POST or None)
    emergency_contact_details_form = EmergencyContactDetailsForm(request.POST or None)
    previous_academic_info_form = PreviousAcademicInfoForm(request.POST or None)
    previous_academic_certificate_form = PreviousAcademicCertificateForm(request.POST or None, request.FILES or None)

    registration_no = None  # To hold and pass the registration number

    if request.method == 'POST':
        # Check if all forms are valid
        if (
            academic_info_form.is_valid() and
            personal_info_form.is_valid() and
            student_address_info_form.is_valid() and
            guardian_info_form.is_valid() and
            emergency_contact_details_form.is_valid() and
            previous_academic_info_form.is_valid() and
            previous_academic_certificate_form.is_valid()
        ):
            try:
                # Save all forms
                personal_info = personal_info_form.save()
                address_info = student_address_info_form.save()
                guardian_info = guardian_info_form.save()
                emergency_contact = emergency_contact_details_form.save()
                previous_academic_info = previous_academic_info_form.save()
                previous_academic_certificate = previous_academic_certificate_form.save()

                # Save academic info with relationships
                academic_info = academic_info_form.save(commit=False)
                academic_info.personal_info = personal_info
                academic_info.address_info = address_info
                academic_info.guardian_info = guardian_info
                academic_info.emergency_contact_info = emergency_contact
                academic_info.previous_academic_info = previous_academic_info
                academic_info.previous_academic_certificate = previous_academic_certificate

                # Ensure a registration number is set
                if not academic_info.registration_no:
                    academic_info.registration_no = AcademicInfo.generate_unique_registration_no()

                academic_info.save()

                registration_no = academic_info.registration_no  # Pass to template

                messages.success(request, f"Student registered successfully! Registration Number: {registration_no}")
                return redirect('student-list')  # Redirect to a student list view
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")

    context = {
        'teacher': teacher,
        'profile': user_profile,
        'academic_info_form': academic_info_form,
        'personal_info_form': personal_info_form,
        'student_address_info_form': student_address_info_form,
        'guardian_info_form': guardian_info_form,
        'emergency_contact_details_form': emergency_contact_details_form,
        'previous_academic_info_form': previous_academic_info_form,
        'previous_academic_certificate_form': previous_academic_certificate_form,
        'registration_no': registration_no,  # Pass registration number to context
    }
    return render(request, 'student/student-registration.html', context)

from account.models import Message
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings

from django.shortcuts import redirect

def student_list(request, teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    teacher = None
    if user_profile.employee_type in ['teacher', 'professor']:
        teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id) if teacher_id else get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    form = StudentSearchForm(request.GET or None, initial={'user_profile': user_profile})
    student_name = request.GET.get('name', None)
    class_info = request.GET.get('class_info', None)
    session_info = request.GET.get('session_info', None)

    queries = Q(is_delete=False)
    if user_profile.employee_type == 'student':
        if not class_info and user_profile.student_class:
            class_info = user_profile.student_class.id
        if not session_info and user_profile.student_session:
            session_info = user_profile.student_session.id
        if not class_info or not session_info:
            context = {
                'form': form,
                'students': AcademicInfo.objects.none(),
                'profile': user_profile,
                'error_message': 'Your profile is missing class or session information. Please contact your HOD.'
            }
            return render(request, 'student/student-list.html', context)

    if student_name:
        queries &= Q(personal_info__name__icontains=student_name)
    if class_info:
        queries &= Q(class_info=class_info)
    if session_info:
        queries &= Q(session_info=session_info)

    students = AcademicInfo.objects.filter(queries, personal_info__userprofile__isnull=False).order_by('-id')

    if user_profile.employee_type == 'student':
        form.fields['class_info'].queryset = ClassInfo.objects.filter(id=user_profile.student_class.id)
        form.fields['session_info'].queryset = Session.objects.filter(id=user_profile.student_session.id)

    if request.method == 'POST':
        recipient_ids = request.POST.getlist('selected_students')
        message_text = request.POST.get('message_text')
        image = request.FILES.get('image', None)

        if not recipient_ids:
            recipient_ids = [student.personal_info.userprofile.id for student in students]

        if message_text and message_text.strip():
            try:
                for recipient_id in recipient_ids:
                    recipient_profile = get_object_or_404(UserProfile, id=recipient_id)
                    recipient = recipient_profile.user
                    sender_profile = user_profile
                    sender = request.user

                    # Save message to the database
                    Message.objects.create(
                        sender=sender,
                        recipient=recipient,
                        message_text=message_text,
                        image=image
                    )

                    # Send email notification
                    subject = "Karmayogi Institute of Technology"
                    domain = request.META['HTTP_HOST']
                    link = f"http://{domain}/messages/"
                    email_message = f"""
                        Hello {recipient_profile.name},

                        You have received a new message from {sender_profile.name}:

                        "{message_text}"

                        Click the link below to view your messages:
                        {link}

                        Best regards,
                        {settings.DEFAULT_FROM_EMAIL}
                    """
                    send_mail(
                        subject,
                        email_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient.email],
                        fail_silently=False,
                    )

                messages.success(request, f"Message sent successfully to {len(recipient_ids)} student(s).")
            except Exception as e:
                messages.error(request, f"Failed to send message: {e}")
        else:
            messages.error(request, "Please enter a message.")

        # Redirect after processing the POST request
        return redirect('student-list')  # Replace 'student-list' with the correct URL name of your view

    context = {
        'teacher': teacher,
        'form': form,
        'students': students,
        'profile': user_profile,
    }
    return render(request, 'student/student-list.html', context)




from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from collections import defaultdict
import json
from attendance.models import StudentAttendance, StudentMark, EnrolledStudent
from attendance.forms import SearchEnrolledStudentForm, MarkForm
from result.models import SubjectRegistration


@login_required(login_url='login')
def student_attendance(request, student_id):
    student = get_object_or_404(EnrolledStudent, id=student_id)

    # Attendance records and counts
    attendance_records = StudentAttendance.objects.filter(student=student)
    attendance_summary = {}
    subject_attendance_counts = defaultdict(lambda: {'present': 0, 'absent': 0})

    for record in attendance_records:
        subject = record.subject.subject_name
        if subject not in attendance_summary:
            attendance_summary[subject] = {'present': 0, 'absent': 0}
        if record.status == 1:
            attendance_summary[subject]['present'] += 1
        else:
            attendance_summary[subject]['absent'] += 1
        subject_attendance_counts[subject]['present'] += 1 if record.status == 1 else 0
        subject_attendance_counts[subject]['absent'] += 1 if record.status == 0 else 0

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

    context = {
        'student': student,
        'attendance_summary': attendance_summary,
        'subject_attendance_counts': json.dumps(subject_attendance_counts),
        'subject_attendance_percentages': subject_attendance_percentages,
    }

    return render(request, 'student/student-attendance.html', context)

@login_required(login_url='login')
def student_marks(request, student_id):
    student = get_object_or_404(EnrolledStudent, id=student_id)

    # Filter handling
    search_query = request.GET.get('search', '')
    filter_form = SearchEnrolledStudentForm(request.GET or None)

    marks_records = StudentMark.objects.filter(student=student)

    if search_query:
        marks_records = marks_records.filter(
            Q(subject__subject_name__icontains=search_query) |
            Q(mark_type__icontains=search_query)
        )

    mark_type = request.GET.get('mark_type')
    if mark_type:
        marks_records = marks_records.filter(mark_type=mark_type)

    subject = request.GET.get('subject')
    if subject:
        marks_records = marks_records.filter(subject__subject_name=subject)

    context = {
        'student': student,
        'filter_form': filter_form,
        'marks_data': marks_records,
        'search_query': search_query,
    }

    return render(request, 'student/student-marks.html', context)

def student_profile(request, reg_no, teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    teacher = None  # Initialize teacher to None
    if user_profile.employee_type in ['teacher', 'professor']:
        teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id) if teacher_id else \
                  get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)

    student = get_object_or_404(AcademicInfo, registration_no=reg_no)
    
    context = {
        'teacher': teacher,
        'profile': user_profile,
        'student': student
    }
    return render(request, 'student/student-profile.html', context)

def student_edit(request, reg_no, teacher_id=None):
    # Get the user's profile
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Deny access if the user is a student
    if user_profile.employee_type == 'student':
        return redirect('permission_denied')  # or render('error/permission_denied.html')
    
    # Proceed if the user is a teacher or professor
    if user_profile.employee_type in ['teacher', 'professor']:
        if not teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
    
    # Fetch the student's academic record by registration number
    student = get_object_or_404(AcademicInfo, registration_no=reg_no)
    
    # Initialize the forms with the student's existing data
    academic_info_form = AcademicInfoForm(instance=student)
    personal_info_form = PersonalInfoForm(instance=student.personal_info)
    student_address_info_form = StudentAddressInfoForm(instance=student.address_info)
    guardian_info_form = GuardianInfoForm(instance=student.guardian_info)
    emergency_contact_details_form = EmergencyContactDetailsForm(instance=student.emergency_contact_info)
    previous_academic_info_form = PreviousAcademicInfoForm(instance=student.previous_academic_info)
    previous_academic_certificate_form = PreviousAcademicCertificateForm(instance=student.previous_academic_certificate)

    # If the form has been submitted (POST request)
    if request.method == 'POST':
        academic_info_form = AcademicInfoForm(request.POST, instance=student)
        personal_info_form = PersonalInfoForm(request.POST, request.FILES, instance=student.personal_info)
        student_address_info_form = StudentAddressInfoForm(request.POST, instance=student.address_info)
        guardian_info_form = GuardianInfoForm(request.POST, instance=student.guardian_info)
        emergency_contact_details_form = EmergencyContactDetailsForm(request.POST, instance=student.emergency_contact_info)
        previous_academic_info_form = PreviousAcademicInfoForm(request.POST, instance=student.previous_academic_info)
        previous_academic_certificate_form = PreviousAcademicCertificateForm(request.POST, request.FILES, instance=student.previous_academic_certificate)
        
        # Check if all forms are valid before saving
        if (academic_info_form.is_valid() and personal_info_form.is_valid() and student_address_info_form.is_valid() and 
            guardian_info_form.is_valid() and emergency_contact_details_form.is_valid() and 
            previous_academic_info_form.is_valid() and previous_academic_certificate_form.is_valid()):
            
            # Save each part of the form data
            s1 = personal_info_form.save()
            s2 = student_address_info_form.save()
            s3 = guardian_info_form.save()
            s4 = emergency_contact_details_form.save()
            s5 = previous_academic_info_form.save()
            s6 = previous_academic_certificate_form.save()
            
            # Save the academic info with the associated forms
            academic_info = academic_info_form.save(commit=False)
            academic_info.personal_info = s1
            academic_info.address_info = s2
            academic_info.guardian_info = s3
            academic_info.emergency_contact_info = s4
            academic_info.previous_academic_info = s5
            academic_info.previous_academic_certificate = s6
            academic_info.save()
            
            # Redirect to the student list page upon successful save
            return redirect('student-list')

    # Prepare the context for rendering the template
    context = {
        'teacher': teacher,
        'profile': user_profile,
        'academic_info_form': academic_info_form,
        'personal_info_form': personal_info_form,
        'student_address_info_form': student_address_info_form,
        'guardian_info_form': guardian_info_form,
        'emergency_contact_details_form': emergency_contact_details_form,
        'previous_academic_info_form': previous_academic_info_form,
        'previous_academic_certificate_form': previous_academic_certificate_form
    }
    
    # Render the edit page
    return render(request, 'student/student-edit.html', context)



logger = logging.getLogger(__name__)

@login_required(login_url='login')
def student_delete(request, reg_no):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type='professor')

    if user_profile.employee_type != 'professor':
        messages.error(request, "You do not have permission to delete this student please contact to Principal Sir ")
        return redirect('student-list')

    try:
        student = get_object_or_404(AcademicInfo, registration_no=reg_no)
        student.is_deleted = True
        student.save()
        messages.success(request, f"Student deleted successfully. <a href='{reverse('student-undo-delete', args=[student.registration_no])}'>Undo</a>")
        logger.info(f"Student with registration number {reg_no} marked as deleted by user {request.user}")
    except Exception as e:
        messages.error(request, f"Error deleting student: {e}")
        logger.error(f"Error deleting student with registration number {reg_no}: {e}")

    return redirect('student-list')



@login_required(login_url='login')
def student_undo_delete(request, reg_no):
    try:
        student = get_object_or_404(AcademicInfo, registration_no=reg_no)
        student.is_deleted = False  # Mark student as not deleted
        student.save()
        messages.success(request, "Student successfully restored.")
        logger.info(f"Student with registration number {reg_no} restored by user {request.user}")
    except Exception as e:
        messages.error(request, f"Error restoring student: {e}")
        logger.error(f"Error restoring student with registration number {reg_no}: {e}")

    return redirect('student-list')


def student_search(request,teacher_id=None):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.employee_type in ['teacher', 'professor']:
        if not teacher_id:
            teacher = get_object_or_404(TeacherPersonalInfo, address__userprofile=user_profile)
        else:
            teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)

    # Check if user is not a professor, redirect if necessary
    if user_profile.employee_type not in  ['teacher', 'professor']:
        return redirect('login')  # You should define your login URL here

    form = StudentSearchForm(request.GET or None)
    cls_name = request.GET.get('class_info', None)
    session_info = request.GET.get('session_info', None)
    reg_no = request.GET.get('registration_no', None)
    student_name = request.GET.get('name', None)
    student = AcademicInfo.objects.none()

    queries = Q()

    if reg_no:
        if not reg_no.isdigit():
            return redirect('/student/student-search/?error=invalid_registration_no')
        queries &= Q(registration_no=reg_no)

    if cls_name and session_info:  # Both cls_name and session_info are required
        queries &= Q(class_info=cls_name, session_info=session_info)
    
    
    if cls_name :  # Both cls_name and session_info are required
        queries &= Q(class_info=cls_name)

    if student_name:
        queries &= Q(personal_info__name__icontains=student_name)

    if queries:
        student = AcademicInfo.objects.filter(queries)

    context = {
        'teacher':teacher,
        'profile': user_profile,
        'form': form,
        'student': student
    }
    return render(request, 'student/student-search.html', context)
def enrolled_student(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor', 'teacher'])

    forms = EnrolledStudentForm(request.GET)  # Populate form with GET data
    cls = request.GET.get('class_name', None)
    status = request.GET.get('status', None)

    # Build the queryset
    student_query = AcademicInfo.objects.all()

    if cls:
        student_query = student_query.filter(class_info=cls)

    if status and status != '':
        student_query = student_query.filter(status=status)

    context = {
        'profile': user_profile,
        'forms': forms,
        'student': student_query
    }
    return render(request, 'student/enrolled.html', context)
def student_enrolled(request, reg):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor','teacher'])
        
    student = AcademicInfo.objects.get(registration_no=reg)
    forms = StudentEnrollForm()
    if request.method == 'POST':
        forms = StudentEnrollForm(request.POST)
        if forms.is_valid():
            roll = forms.cleaned_data['roll_no']
            class_name = forms.cleaned_data['class_name']
            EnrolledStudent.objects.create(class_name=class_name, student=student, roll=roll)
            student.status = 'enrolled'
            student.save()
            return redirect('enrolled-student-list')
    context = {
        'profile' : user_profile,
        'student': student,
        'forms': forms
    }
    return render(request, 'student/student-enrolled.html', context)



def enrolled_student_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor', 'teacher'])

    student = EnrolledStudent.objects.all()
    forms = SearchEnrolledStudentForm(request.GET or None)

    class_name = request.GET.get('reg_class', None)
    session_year = request.GET.get('session_year', None)
    roll = request.GET.get('roll_no', None)

    # Check if roll number is provided without class_name or session_year
    if roll and not (class_name and session_year):
        forms.add_error(None, 'Please provide both class and session year to search by roll number.')
    
    elif class_name and session_year:
        # Filter by class_name and session_year
        student = EnrolledStudent.objects.filter(class_name=class_name, session_year=session_year)

        # If roll number is also provided, further filter by roll number
        if roll:
            student = student.filter(roll=roll)  # Corrected 'roll_no' to 'roll'

    context = {
        'profile': user_profile,
        'forms': forms,
        'student': student
    }
    return render(request, 'student/enrolled-student-list.html', context)


@login_required(login_url='login')
def student_inbox(request):
    """Display all messages received by the student and count unread messages."""
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = messages.filter(is_read=False).count()  # Count unread messages
    context = {
        'messages': messages,
        'unread_count': unread_count,  # Add unread count to context
    }
    return render(request, 'student/inbox.html', context)


@login_required(login_url='login')
def student_read_message(request, message_id):
    """Mark a message as read and display its details for students."""
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if not message.is_read:
        message.is_read = True
        message.save()

    context = {'message': message}
    return render(request, 'student/message_detail.html', context)
