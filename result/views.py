from django.shortcuts import render, redirect, get_object_or_404
from account.models import UserProfile
from academic.models import ClassRegistration,Session
from .forms import SubjectRegistrationForm, ClassSelectSubjectListForm
from student.models import AcademicInfo
from .models import SubjectRegistration

def add_subject(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type='professor')

    # Allow access to both professors and teachers
    if user_profile.employee_type not in ['professor', 'teacher']:
        return redirect('login')

    if request.method == 'POST':
        subject_form = SubjectRegistrationForm(request.POST, request.FILES)
        if subject_form.is_valid():
            subject_form.save()
            return redirect('subject-list')
    else:
        subject_form = SubjectRegistrationForm()

    context = {
        'subject_form': subject_form,
        'profile': user_profile,
    }

    return render(request, 'result/add-subject.html', context)

def add_subject(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, employee_type='professor')

    # Allow access to both professors and teachers
    if user_profile.employee_type not in ['professor', 'teacher']:
        return redirect('login')

    if request.method == 'POST':
        subject_form = SubjectRegistrationForm(request.POST, request.FILES)
        if subject_form.is_valid():
            subject_form.save()
            return redirect('subject-list')
    else:
        subject_form = SubjectRegistrationForm()

    context = {
        'subject_form': subject_form,
        'profile': user_profile,
    }

    return render(request, 'result/add-subject.html', context)


def subject_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('login')

    subjects = SubjectRegistration.objects.all()  # Show all subjects to everyone
    form = None

    if user_profile.employee_type == 'student':
        # Students will see subjects based on their class and session
        student_class = user_profile.student_class
        student_session = user_profile.student_session

        if student_class and student_session:
            try:
                class_registration = ClassRegistration.objects.get(
                    class_name=student_class,
                    session=student_session
                )
                subjects = SubjectRegistration.objects.filter(
                    select_class=class_registration,
                    session_info=student_session
                )
            except ClassRegistration.DoesNotExist:
                subjects = SubjectRegistration.objects.none()

    elif user_profile.employee_type in ['professor', 'teacher']:
        form = ClassSelectSubjectListForm(request.GET or None)
        select_class = request.GET.get('select_class', None)
        selected_session = request.GET.get('session', None)

        if select_class and selected_session:
            cls = get_object_or_404(ClassRegistration, id=select_class)
            session_obj = get_object_or_404(Session, id=selected_session)
            subjects = SubjectRegistration.objects.filter(select_class=cls, session_info=session_obj)

    context = {
        'profile': user_profile,
        'form': form,
        'subjects': subjects,
        'no_subjects_found': subjects.count() == 0,
    }
    return render(request, 'result/subject-list.html', context)


def subject_detail(request, pk):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('login')

    # Allow both students and professors/teachers to access the subject details
    if user_profile.employee_type == 'student':
        # Retrieve student class and session
        student_class = user_profile.student_class
        student_session = user_profile.student_session

        # Ensure class and session are available
        if not student_class or not student_session:
            return render(request, 'result/subject_detail.html', {
                'profile': user_profile,
                'error': 'Class or session information is missing for the student.',
            })

        # Ensure the class registration exists
        try:
            class_registration = ClassRegistration.objects.get(
                class_name=student_class,
                session=student_session
            )
        except ClassRegistration.DoesNotExist:
            return render(request, 'result/subject_detail.html', {
                'profile': user_profile,
                'error': 'Class registration not found for the specified class and session.',
            })

        # Get subject for the student’s class and session
        subject = get_object_or_404(
            SubjectRegistration,
            pk=pk,
            select_class=class_registration,
            session_info=student_session
        )

    elif user_profile.employee_type in ['professor', 'teacher']:
        # Professors and teachers can access any subject
        subject = get_object_or_404(SubjectRegistration, pk=pk)

    else:
        # Unauthorized user redirects to login
        return redirect('login')

    form = ClassSelectSubjectListForm()  # This could be used for selecting subjects in the future

    return render(request, 'result/subject_detail.html', {
        'subject': subject,
        'profile': user_profile,
        'form': form,
    })