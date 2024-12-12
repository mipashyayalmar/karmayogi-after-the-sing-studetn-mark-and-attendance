from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout as auth_logout 
import student
import teacher
import employee
import academic
from .forms import AdminLoginForm, ProfileForm
from django.contrib import messages
from django.conf.urls import handler404



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import AdminLoginForm
from .models import UserProfile

# Custom CSRF failure handler
def csrf_failure(request, reason=""):
    if request.user.is_authenticated:
        auth_logout(request)  # Log out the user if a CSRF failure occurs
    messages.error(request, "CSRF validation failed. Please try again.")
    return redirect('login')  # Redirect to the login page


def login_home(request):
    if request.user.is_authenticated:
        try:
            # Check if the user profile exists
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Redirect based on employee type
            if user_profile.employee_type == 'professor':
                return redirect('professor_profiles')  # Redirect to professor profile page
            elif user_profile.employee_type == 'teacher':
                return redirect('teacher_profiles')  # Redirect to teacher profile page
            elif user_profile.employee_type == 'student':
                return redirect('student_profiles')  # Redirect to student profile page
            elif user_profile.employee_type == 'employee':
                return redirect('employee_profiles')  # Redirect to employee profile page
            else:
                return redirect('home')  # Redirect to a default home page
        except UserProfile.DoesNotExist:
            # Redirect to permission denied page if UserProfile doesn't exist
            return render(request, 'error/permission_denied.html')

    # Handle the login form if the user is not authenticated
    forms = AdminLoginForm()
    error_message = None  # Initialize error_message variable

    if request.method == 'POST':
        forms = AdminLoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                try:
                    # Check if the user profile exists after login
                    user_profile = UserProfile.objects.get(user=request.user)
                    
                    # Redirect based on employee type
                    if user_profile.employee_type == 'professor':
                        return redirect('professor_profiles')
                    elif user_profile.employee_type == 'teacher':
                        return redirect('teacher_profiles')
                    elif user_profile.employee_type == 'student':
                        return redirect('student_profiles')
                    elif user_profile.employee_type == 'employee':
                        return redirect('employee_profiles')
                    else:
                        return redirect('home')
                except UserProfile.DoesNotExist:
                    # Redirect to permission denied page if UserProfile doesn't exist
                    return render(request, 'error/permission_denied.html')
            else:
                # Set an error message if login fails
                error_message = "Invalid username or password. Please try again."

    # Render the login page with the form and error message
    context = {'forms': forms, 'error_message': error_message}
    return render(request, 'administration/login.html', context)

def logout(request):
    auth_logout(request)  
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


@login_required(login_url='login')
def home_page(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type=['professor','teacher'])

    # if user_profile.employee_type != 'professor':
    #     return redirect('login') 
    total_student = student.models.AcademicInfo.objects.count()
    total_teacher = teacher.models.PersonalInfo.objects.count()
    total_employee = employee.models.PersonalInfo.objects.count()
    total_class = academic.models.ClassRegistration.objects.count()
    context = {
        'student': total_student,
        'teacher': total_teacher,
        'employee': total_employee,
        'total_class': total_class,
        'profile' : user_profile,
        
    }
    return render(request, 'professor/home', context)

@login_required
def profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        return redirect('profile')  
    context = {
        'profile': profile
    }
    return render(request, 'account/profile.html', context)



@login_required
def update_profile_2(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        return redirect('profile')  
    context = {
        'profile': profile
    }
    return render(request, 'account/profile.html', context)


@login_required
def update_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        messages.info(request, "Please update your profile information.")
        return redirect('update_profile_2')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
        else:
            print(form.errors)  # Debugging: print form errors to the console
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'account/update-profile.html', context)




def permission_denied(request):
    try:
        user_profile = request.user.userprofile
        profile_type = user_profile.employee_type 
    except UserProfile.DoesNotExist:
        messages.info(request, "Please complete your profile to access this page.")
        return redirect('update_profile') 

    context = {
        'profile_type': profile_type,
        'user_profile': user_profile,
    }

    return render(request, 'error/permission_denied.html', context)



@login_required(login_url='login')
def create_profile(request):
    if request.method == "POST":
        # Get current user's profile
        user_profile = UserProfile.objects.get(user=request.user)

        # Update profile fields from the form data
        user_profile.student_class = request.POST.get('student_class')
        user_profile.student_session = request.POST.get('student_session')
        user_profile.department = request.POST.get('department')

        # Mark the profile as complete (if using the field)
        user_profile.is_complete = True
        user_profile.save()

        # Redirect to student profile or another page
        return redirect('student_profile')

    return render(request, 'student/create_profile.html')
