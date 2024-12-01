from django import forms
from academic.models import ClassRegistration, Session
from result.models import SubjectRegistration
from .models import StudentAttendance, StudentMark
from django.forms import DateInput


class SearchEnrolledStudentForm(forms.Form):
    reg_class = forms.ModelChoiceField(
        queryset=ClassRegistration.objects.all(), required=False, label="Class"
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(), required=False, label="Session"
    )
    subject = forms.ModelChoiceField(
        queryset=SubjectRegistration.objects.none(), required=False, label="Subject"
    )
    mark_type = forms.ChoiceField(
        choices=[('', 'Select Mark Type')],  # Initially empty
        required=False,
        label="Mark Type"
    )
    attendance_date = forms.DateField(
        label="Attendance Date (Single)",
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    start_date = forms.DateField(
        label="Start Date",
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        label="End Date",
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    registration_no = forms.CharField(
        label="Registration Number", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Enter Registration No'})
    )

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        # Auto-fill fields for students if necessary
        if user_profile and user_profile.employee_type == 'student':
            self.fields['reg_class'].initial = user_profile.student_class
            self.fields['session'].initial = user_profile.student_session

        reg_class_id = self.data.get('reg_class')
        session_id = self.data.get('session')

        # Dynamically filter the subjects based on class and session
        if reg_class_id and session_id:
            self.fields['subject'].queryset = SubjectRegistration.objects.filter(
                select_class_id=reg_class_id,
                session_info_id=session_id
            ).distinct()

        # Dynamically filter mark types based on selected class and session
        if reg_class_id and session_id:
            # Find distinct mark types for the class and session
            mark_types = StudentMark.objects.filter(
                student__class_name=reg_class_id, student__session_year=session_id
            ).values_list('mark_type', flat=True).distinct()

            # Set the choices for mark_type dynamically
            self.fields['mark_type'].choices += [(mt, mt) for mt in mark_types]

        # Apply Bootstrap styling to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class AttendanceForm(forms.Form):
    select_class = forms.ModelChoiceField(queryset=ClassRegistration.objects.all(), label="Class", required=False)
    session_year = forms.ModelChoiceField(queryset=Session.objects.all(), label="Session", required=False)
    subject = forms.ModelChoiceField(queryset=SubjectRegistration.objects.none(), label="Subject", required=False)
    attendance_date = forms.DateField(label="Attendance Date", widget=DateInput(attrs={'type': 'date'}), required=True)
    filter_date = forms.DateField(label="Filter Attendance Date", widget=DateInput(attrs={'type': 'date'}), required=False)

    def __init__(self, *args, **kwargs):
        class_id = kwargs.pop('class_id', None)
        session_year = kwargs.pop('session_year', None)
        user_profile = kwargs.pop('user_profile', None)

        super().__init__(*args, **kwargs)

        if user_profile and user_profile.employee_type == 'student':
            # Set initial values and disable fields for students
            self.fields['select_class'].initial = user_profile.student_class
            self.fields['session_year'].initial = user_profile.student_session
            self.fields['select_class'].disabled = True
            self.fields['session_year'].disabled = True

            self.fields['subject'].queryset = SubjectRegistration.objects.filter(
                select_class=user_profile.student_class,
                session_info=user_profile.student_session
            ).distinct()
            self.fields['subject'].initial = self.fields['subject'].queryset.first()
        elif class_id and session_year:
            # Set subject queryset based on class and session for non-students
            self.fields['subject'].queryset = SubjectRegistration.objects.filter(
                select_class__id=class_id,
                session_info__id=session_year
            ).distinct()

        # Apply Bootstrap styling to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})




class MarkForm(forms.ModelForm):
    subject = forms.ModelChoiceField(queryset=SubjectRegistration.objects.none(), label="Subject", required=True)
    total_score = forms.IntegerField(required=False, label="Total Score")
    mark_type = forms.CharField(label="Mark Type", required=True)
    exam_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}), required=True, label="Exam Date"
    )

    class Meta:
        model = StudentMark
        fields = ['subject', 'exam_date', 'mark_type', 'score', 'total_score']
        widgets = {'exam_date': DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, class_id=None, session_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Filter subjects based on class and session if provided
        if class_id and session_year:
            self.fields['subject'].queryset = SubjectRegistration.objects.filter(
                select_class__id=class_id, session_info__id=session_year
            ).distinct()
        else:
            self.fields['subject'].queryset = SubjectRegistration.objects.all()

    def clean_exam_date(self):
        exam_date = self.cleaned_data.get('exam_date')
        if not exam_date:
            raise forms.ValidationError("This field is required and must be a valid date in YYYY-MM-DD format.")
        return exam_date