from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms
from .models import District, Upazilla, Union, PersonalInfo
from account.models import UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import logging
from django.http import HttpResponseForbidden
from employee.models import PersonalInfo as EmployeePersonalInfo
from teacher.models import PersonalInfo as TeacherPersonalInfo
from student.models import AcademicInfo

@login_required(login_url='login')
def load_upazilla(request):
    user_profile = UserProfile.objects.get(user=request.user)
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

@login_required(login_url='login')
def employee_registration(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.employee_type == 'professor':
        form = forms.PersonalInfoForm()
        address_forms = forms.AddressInfoForm()
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
            if form.is_valid() and address_form.is_valid() and education_form.is_valid() and training_form.is_valid() and job_form.is_valid() and experience_form.is_valid():
                personal_info = form.save()
                address_info = address_form.save(commit=False)
                address_info.address = personal_info
                address_info.save()
                education_info = education_form.save(commit=False)
                education_info.education = personal_info
                education_info.save()
                training_info = training_form.save(commit=False)
                training_info.training = personal_info
                training_info.save()
                job_info = job_form.save(commit=False)
                job_info.job = personal_info
                job_info.save()
                experience_info = experience_form.save(commit=False)
                experience_info.experience = personal_info
                experience_info.save()
                return redirect('employee-list')

        context = {
            'form': form,
            'address_forms': address_forms,
            'education_form': education_form,
            'training_form': training_form,
            'job_form': job_form,
            'experience_form': experience_form,
            'profile': user_profile
        }
        return render(request, 'employee/employee-registration.html', context)
    else:
        return render(request, 'error/permission_denied.html')



@login_required(login_url='login')
def employee_list(request, employee_id=None):  # employee_id is passed here as an argument
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # If employee_id is provided, filter by that employee
    if employee_id:
        employees = EmployeePersonalInfo.objects.filter(id=employee_id)
    else:
        # Case for professor with unrestricted access
        if user_profile.employee_type == 'professor':
            employees = EmployeePersonalInfo.objects.all()

        # Case for teacher with department-based filtering
        elif user_profile.employee_type in ['teacher', 'employee']:
            employees = EmployeePersonalInfo.objects.filter(job__department=user_profile.department)

        # Case for student with department-based filtering
        elif user_profile.employee_type == 'student':
            employees = EmployeePersonalInfo.objects.filter(job__department=user_profile.department)

        # Redirect if user type is not allowed to view employee list
        else:
            return render(request, 'error/permission_denied.html')

    # Prepare context and render the employee list page
    context = {
        'employees': employees,
        'profile': user_profile,
    }
    return render(request, 'employee/employee-list.html', context)
       
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def employee_profile(request, employee_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Fetch the employee details based on the employee_id
    employee = get_object_or_404(EmployeePersonalInfo, id=employee_id)

    # Check if the logged-in user is allowed to view the profile
    # All employees, professors, and teachers can view any profile, including their own
    if user_profile.employee_type in ['professor', 'teacher', 'employee']:

        # Ensure an employee can view their own profile as well as others'
        if employee.id == user_profile.id or user_profile.employee_type in ['professor', 'teacher','employee']:
            context = {
                'employee': employee,
                'profile': user_profile,
                'employee_id': employee_id  # Pass employee_id to template
            }
            return render(request, 'employee/employee-profile.html', context)
        else:
            # If an employee tries to view someone else's profile, log unauthorized access
            logger.warning(f"Unauthorized access attempt by {request.user.username} to employee profile {employee_id}")
            return redirect('permission_denied')
    else:
        # Log the unauthorized access attempt (for any invalid employee type)
        logger.warning(f"Unauthorized access attempt by {request.user.username} to employee profile {employee_id}")
        return redirect('permission_denied')


@login_required(login_url='login')
def employee_delete(request, employee_id):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.employee_type in ['professor', 'teacher']:
        try:
            employee = get_object_or_404(PersonalInfo, id=employee_id)
            employee.delete()
            messages.success(request, "Employee deleted successfully.")
            logger.info(f"Employee with id {employee_id} deleted successfully by user {request.user}")
        except Exception as e:
            messages.error(request, f"Error deleting employee: {e}")
            logger.error(f"Error deleting employee with id {employee_id}: {e}")
        return redirect('employee-list')
    else:
        messages.error(request, "You do not have permission to delete this employee.")
        return render(request, 'error/permission_denied.html')

@login_required(login_url='login')
def employee_edit(request, employee_id):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.employee_type in ['professor', 'teacher']:
        employee = PersonalInfo.objects.get(id=employee_id)
        form = forms.PersonalInfoForm(instance=employee)
        address_forms = forms.AddressInfoForm(instance=employee.address)
        education_form = forms.EducationInfoForm(instance=employee.education)
        training_form = forms.TrainingInfoForm(instance=employee.training)
        job_form = forms.JobInfoForm(instance=employee.job)
        experience_form = forms.ExperienceInfoForm(instance=employee.experience)
        if request.method == 'POST':
            form = forms.PersonalInfoForm(request.POST, request.FILES, instance=employee)
            address_form = forms.AddressInfoForm(request.POST, instance=employee.address)
            education_form = forms.EducationInfoForm(request.POST, instance=employee.education)
            training_form = forms.TrainingInfoForm(request.POST, instance=employee.training)
            job_form = forms.JobInfoForm(request.POST, instance=employee.job)
            experience_form = forms.ExperienceInfoForm(request.POST, instance=employee.experience)
            if form.is_valid() and address_form.is_valid() and education_form.is_valid() and training_form.is_valid() and job_form.is_valid() and experience_form.is_valid():
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
                return redirect('employee-list')
        context = {
            'form': form,
            'address_form': address_forms,
            'education_form': education_form,
            'training_form': training_form,
            'job_form': job_form,
            'experience_form': experience_form,
            'profile': user_profile
        }
        return render(request, 'employee/employee-edit.html', context)
    else:
        return render(request, 'error/permission_denied.html')


from .forms import EmployeeMessageForm 
from .models import EmployeeMessage  # Add this import


@login_required(login_url='login')
def send_message(request, employee_id=None):
    # Get the logged-in user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Ensure the user is allowed to send messages
    if user_profile.employee_type not in ['professor', 'teacher', 'employee']:
        return render(request, 'error/permission_denied.html')

    # Check if employee_id is provided in the URL; otherwise, fetch the employee based on the criteria
    if employee_id:
        # Fetch the employee with the provided employee_id
        employee = get_object_or_404(EmployeePersonalInfo, id=employee_id)
    else:
        # If no employee_id is provided, you could fetch employees dynamically (e.g., first one or from a list)
        # For now, just to prevent errors, fetching the first employee
        employee = EmployeePersonalInfo.objects.first()  # This can be customized to select based on other criteria

    if request.method == 'POST':
        message_text = request.POST.get('message_text')

        # Check if an image is uploaded
        image = request.FILES.get('image')

        # Create and save the message
        message = EmployeeMessage(
            employee=employee,
            sender=user_profile,
            message_text=message_text,
            image=image if image else None  # Save the image if provided
        )
        message.save()

        # Provide feedback to the user
        messages.success(request, f"Message sent to {employee.name}.")

        # Redirect to the employee list or profile after sending the message
        return redirect('employee-list')  # or 'employee_profile' if you want to stay on the profile page

    return redirect('employee-list')


from django.http import JsonResponse


@login_required(login_url='login')
def employee_messages(request, employee_id):
    # Fetch the employee and their messages
    employee = get_object_or_404(PersonalInfo, id=employee_id)
    messages_list = EmployeeMessage.objects.filter(employee=employee).order_by('-created_at')  # All messages

    # Fetch the logged-in user's profile
    user_profile = request.user.userprofile

    # Permission check: Ensure only valid users can access messages
    if user_profile.employee_type not in ['employee']:
        return render(request, 'error/permission_denied.html')

    # Check if a message click happened (using GET)
    message_id = request.GET.get('message_id')
    if message_id and message_id != 'null':  # Make sure message_id is not null
        try:
            # Try to fetch and mark the message as read
            message = get_object_or_404(EmployeeMessage, id=message_id, employee=employee)
            message.is_read = True
            message.save()
        except ValueError:
            # Handle the case where message_id is invalid
            pass
        return redirect('employee_messages', employee_id=employee_id)

    # Count unread messages for this employee
    unread_count = messages_list.filter(is_read=False).count()

    # Pass employee profile, messages, and unread count to the context
    context = {
        'employee': employee,
        'messages': messages_list,
        'profile': user_profile,
        'total_unread': unread_count,  # Include unread count
    }
    return render(request, 'employee/employee_messages.html', context)
@login_required(login_url='login')
def messages_list(request):
    # Fetch all messages for the logged-in user
    user_profile = request.user.userprofile
    messages = EmployeeMessage.objects.filter(sender=user_profile).order_by('-created_at')

    # Count unread messages
    total_unread = messages.filter(is_read=False).count()

    context = {
        'messages': messages,
        'total_unread': total_unread,
        'profile': user_profile,
    }
    return render(request, 'employee/employee_messages.html', context)