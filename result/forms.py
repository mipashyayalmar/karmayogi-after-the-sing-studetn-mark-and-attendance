from django import forms
from .models import SubjectRegistration, ClassRegistration,Session


class SubjectRegistrationForm(forms.ModelForm):
    class Meta:
        model = SubjectRegistration
        fields = '__all__'

        widgets = {
            'select_class': forms.Select(attrs={'class': 'form-control'}),
            'session_info': forms.Select(attrs={'class': 'form-control'}),
            'userprofile': forms.Select(attrs={'class': 'form-control'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'pass_mark': forms.NumberInput(attrs={'class': 'form-control'}),
            'syllabus_picture': forms.FileInput(attrs={'class': 'form-control'})  
        }


class ClassSelectSubjectListForm(forms.Form):
    select_class = forms.ModelChoiceField(
        queryset=ClassRegistration.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

