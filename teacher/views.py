from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
import logging
from . import forms
from .models import District, Upazilla, Union, PersonalInfo
from account.models import UserProfile
from teacher.models import PersonalInfo as TeacherPersonalInfo

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def load_upazilla(request):
    """Load the Upazilla and Union based on the selected district."""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.employee_type == 'professor':
        district_id = request.GET.get('district')
        upazilla = Upazilla.objects.filter(district_id=district_id).order_by('name')
        
        upazilla_id = request.GET.get('upazilla')
        union = Union.objects.filter(upazilla_id=upazilla_id).order_by('name')
        
        context = {
            'upazilla': upazilla,
            'union': union,
            'profile': user_profile
        }
        return render(request, 'others/upazilla_dropdown_list_options.html', context)
    else:
        return render(request, 'error/permission_denied.html')

@login_required(login_url='login')
def teacher_registration(request):
    """Handle the registration of teachers."""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.employee_type == 'professor':
            form = forms.PersonalInfoForm()
            address_form = forms.AddressInfoForm()
            education_form = forms.EducationInfoForm()
            training_form = forms.TrainingInfoForm()
            job_form = forms.JobInfoForm()
            experience_form = forms.ExperienceInfoForm()

            if request.method == 'POST':
                form = forms.PersonalInfoForm(request.POST, request.FILES)
                address_form = forms.AddressInfoForm(request.POST)
                education_form = forms.EducationInfoForm(request.POST)
                training_form = forms.TrainingInfoForm(request.POST)
                job_form = forms.JobInfoForm(request.POST)
                experience_form = forms.ExperienceInfoForm(request.POST)

                if (form.is_valid() and address_form.is_valid() and education_form.is_valid() and
                    training_form.is_valid() and job_form.is_valid() and experience_form.is_valid()):
                    
                    address_info = address_form.save()
                    education_info = education_form.save()
                    training_info = training_form.save()
                    job_info = job_form.save()
                    experience_info = experience_form.save()

                    personal_info = form.save(commit=False)
                    personal_info.address = address_info
                    personal_info.education = education_info
                    personal_info.training = training_info
                    personal_info.job = job_info
                    personal_info.experience = experience_info
                    personal_info.save()

                    return redirect('teacher-list')

            context = {
                'form': form,
                'address_forms': address_form,
                'education_form': education_form,
                'training_form': training_form,
                'job_form': job_form,
                'experience_form': experience_form,
                'profile': user_profile,
            }
            return render(request, 'teacher/teacher-registration.html', context)
        else:
            return render(request, 'error/permission_denied.html')

    except AttributeError as e:
        print(f"Error: {e}")  # Log the error for debugging
        return redirect('teacher-list')  # Redirect to teacher list on failure
from .forms import MessageForm
from account.models import Message

@login_required(login_url='login')
def teacher_list(request, teacher_id=None):
    """Show the list of teachers based on user roles and permissions."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # If a specific teacher ID is provided, filter by that teacher
    if teacher_id:
        teachers = TeacherPersonalInfo.objects.filter(id=teacher_id, is_delete=False)
    else:
        # Case for professor with unrestricted access
        if user_profile.employee_type == 'professor':
            teachers = TeacherPersonalInfo.objects.filter(is_delete=False)

        # Case for teacher with department-based filtering
        elif user_profile.employee_type in ['teacher', 'employee']:
            if not user_profile.department:
                return HttpResponseForbidden("Department information not found.")
            teachers = TeacherPersonalInfo.objects.filter(
                job__department=user_profile.department, is_delete=False
            )

        # Case for student with department-based filtering
        elif user_profile.employee_type == 'student':
            if not user_profile.department:
                return HttpResponseForbidden("Department information not found.")
            teachers = TeacherPersonalInfo.objects.filter(
                job__department=user_profile.department, is_delete=False
            )

        # Redirect if user type is not allowed to view teacher list
        else:
            return render(request, 'error/permission_denied.html')

    # Prepare context and render the teacher list page
    context = {
        'teachers': teachers,
        'profile': user_profile,
    }
    return render(request, 'teacher/teacher-list.html', context)

    
@login_required(login_url='login') 
def teacher_profile(request, teacher_id=None):
    """Display the profile of a specific teacher."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.employee_type in ['teacher', 'professor']:
        if not teacher_id:
            teacher = get_object_or_404(PersonalInfo, address__userprofile=user_profile)
        else:
            teacher = get_object_or_404(PersonalInfo, id=teacher_id)

        # Check if the teacher is associated with the logged-in user or the logged-in user is a professor
        if teacher.address.userprofile == user_profile or user_profile.employee_type == 'professor':
            context = {
                'teacher': teacher,
                'profile': user_profile
            }
            return render(request, 'teacher/teacher-profile.html', context)
        else:
            # Redirect to permission_denied page if not allowed
            return redirect('permission_denied')
    else:
        # Redirect to permission_denied page if the user is not a teacher or professor
        return redirect('permission_denied')


@login_required(login_url='login')
def teacher_delete(request, teacher_id):
    """Allow professors to delete teacher profiles."""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.employee_type == 'professor':
        try:
            teacher = get_object_or_404(PersonalInfo, id=teacher_id)
            teacher.delete()
            messages.success(request, "Teacher deleted successfully.")
            logger.info(f"Teacher with id {teacher_id} deleted successfully by user {request.user}")
        except Exception as e:
            messages.error(request, f"Error deleting teacher: {e}")
            logger.error(f"Error deleting teacher with id {teacher_id}: {e}")
        return redirect('teacher-list')
    else:
        return redirect('permission_denied')


@login_required(login_url='login')
def teacher_edit(request, teacher_id):
    """Allow professors or teachers to edit a teacher's information."""
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.employee_type in ['teacher', 'professor']:
        teacher = PersonalInfo.objects.get(id=teacher_id)

        form = forms.PersonalInfoForm(instance=teacher)
        address_form = forms.AddressInfoForm(instance=teacher.address)
        education_form = forms.EducationInfoForm(instance=teacher.education)
        training_form = forms.TrainingInfoForm(instance=teacher.training)
        job_form = forms.JobInfoForm(instance=teacher.job)
        experience_form = forms.ExperienceInfoForm(instance=teacher.experience)

        if request.method == 'POST':
            form = forms.PersonalInfoForm(request.POST, request.FILES, instance=teacher)
            address_form = forms.AddressInfoForm(request.POST, instance=teacher.address)
            education_form = forms.EducationInfoForm(request.POST, instance=teacher.education)
            training_form = forms.TrainingInfoForm(request.POST, instance=teacher.training)
            job_form = forms.JobInfoForm(request.POST, instance=teacher.job)
            experience_form = forms.ExperienceInfoForm(request.POST, instance=teacher.experience)

            if (form.is_valid() and address_form.is_valid() and education_form.is_valid() and
                training_form.is_valid() and job_form.is_valid() and experience_form.is_valid()):
                address_info = address_form.save()
                education_info = education_form.save()
                training_info = training_form.save()
                job_info = job_form.save()
                experience_info = experience_form.save()

                personal_info = form.save(commit=False)
                personal_info.address = address_info
                personal_info.education = education_info
                personal_info.training = training_info
                personal_info.job = job_info
                personal_info.experience = experience_info
                personal_info.save()

                return redirect('/')

        context = {
            'form': form,
            'address_form': address_form,
            'education_form': education_form,
            'training_form': training_form,
            'job_form': job_form,
            'experience_form': experience_form,
            'profile': user_profile
        }
        return render(request, 'teacher/teacher-edit.html', context)
    else:
        return redirect('permission_denied')
@login_required(login_url='login')
def send_message(request, teacher_id):
    """Allow sending a message to a specific teacher."""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    recipient_teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)  # Include request.FILES for file data
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient_teacher.address.userprofile.user  # Correct field reference
            message.save()
            
            # Assuming the recipient's name is in the UserProfile model.
            recipient_name = recipient_teacher.address.userprofile.name  # Adjust this based on your model structure
            messages.success(request, f"Message sent to {recipient_name}.")
            return redirect('teacher-list')  # Redirect back after sending the message
    else:
        form = MessageForm()

    context = {
        'form': form,
        'profile': user_profile,
    }
    return render(request, 'teacher/teacher-list.html', context)
@login_required(login_url='login')
def inbox(request, teacher_id=None):
    """Display all messages sent to the teacher and count unseen messages."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Ensure the user is either a teacher or professor
    if user_profile.employee_type not in ['teacher', 'professor']:
        messages.error(request, "You do not have permission to access the inbox.")
        return redirect('permission_denied')  # Redirect to permission denied page if not allowed

    # If teacher_id is provided, filter messages for that specific teacher
    if teacher_id:
        # Ensure that the logged-in user has permission to view the teacher's messages
        teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        if user_profile.employee_type == 'professor' or teacher.userprofile == user_profile:
            messages_list = Message.objects.filter(recipient=teacher.userprofile.user).order_by('-created_at')
        else:
            messages.error(request, "You do not have permission to view this teacher's messages.")
            return redirect('permission_denied')
    else:
        # Fetch all messages sent to the logged-in user
        messages_list = Message.objects.filter(recipient=request.user).order_by('-created_at')

    # Count unseen messages
    unseen_count = messages_list.filter(is_read=False).count()

    context = {
        'messages': messages_list,
        'unseen_count': unseen_count,  # Add unseen count to context
        'profile': user_profile,  # Include user profile in context for rendering
    }
    return render(request, 'teacher/inbox.html', context)
@login_required(login_url='login')
def read_message(request, message_id, teacher_id=None):
    """Mark a message as read and display its details."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Ensure the user is either a teacher or professor
    if user_profile.employee_type not in ['teacher', 'professor']:
        messages.error(request, "You do not have permission to view this message.")
        return redirect('permission_denied')  # Redirect to permission denied page if not allowed

    # If teacher_id is provided, ensure the message belongs to that specific teacher
    if teacher_id:
        teacher = get_object_or_404(TeacherPersonalInfo, id=teacher_id)
        if not (user_profile.employee_type == 'professor' or teacher.userprofile == user_profile):
            messages.error(request, "You do not have permission to view this teacher's message.")
            return redirect('permission_denied')

        # Get the message by ID and ensure it belongs to the teacher
        message = get_object_or_404(Message, id=message_id, recipient=teacher.userprofile.user)
    else:
        # Get the message by ID for the logged-in user
        message = get_object_or_404(Message, id=message_id, recipient=request.user)

    # Mark message as read if it's not already read
    if not message.is_read:
        message.is_read = True
        message.save()

    context = {
        'message': message,
        'profile': user_profile,  # Include user profile in context
    }
    return render(request, 'teacher/message_detail.html', context)
