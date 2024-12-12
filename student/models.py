from django.db import models
import random

from academic.models import ClassInfo, ClassRegistration,Session,GuideTeacher, Department
from administration.models import Designation
from account.models import UserProfile
from address.models import District, Upazilla, Union
from account.models import UserProfile


class PersonalInfo(models.Model):
    userprofile = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='student_personal_info'
    )
    name = models.CharField(max_length=100)
    photo = models.ImageField(
        upload_to='student-photos/',
        default='src/img/man.png'  # Path relative to the `static` directory
    )
    
    blood_group_choice = (
        ('a+', 'A+'),
        ('o+', 'O+'),
        ('b+', 'B+'),
        ('ab+', 'AB+'),
        ('a-', 'A-'),
        ('o-', 'O-'),
        ('b-', 'B-'),
        ('ab-', 'AB-')
    )
    blood_group = models.CharField(choices=blood_group_choice, max_length=5)
    date_of_birth = models.DateField()
    
    gender_choice = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = models.CharField(choices=gender_choice, max_length=10)
    phone_no = models.CharField(max_length=11)
    email = models.EmailField(blank=True, null=True)
    birth_certificate_no = models.IntegerField()
    
    religion_choice = (
        ('Hindu', 'Hindu'),
        ('Buddh', 'Buddh'),
        ('Muslim', 'Muslim'),
        ('Sikh', 'Sikh'),
        ('Jain', 'Jain'),
        ('Christian', 'Christian'),
        ('Others', 'Others')
    )
    religion = models.CharField(choices=religion_choice, max_length=45)
    
    nationality_choice = (
        ('Indian', 'Indian'),
        ('Others', 'Others')
    )
    nationality = models.CharField(choices=nationality_choice, max_length=45)

    # New Fields
    mother_tongue = models.CharField(max_length=100, blank=True, null=True )
    candidature_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50, null=True, blank=True)
    ph_type = models.CharField(max_length=50, default='None')
    linguistic_minority = models.CharField(max_length=50, null=True, blank=True,default='none')

    def __str__(self):
        return self.name


class StudentAddressInfo(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    upazilla = models.ForeignKey(Upazilla, on_delete=models.CASCADE)
    union = models.ForeignKey(Union, on_delete=models.CASCADE)
    village = models.TextField()

    def __str__(self):
        return self.village


class GuardianInfo(models.Model):
    father_name = models.CharField(max_length=100)
    father_phone_no = models.CharField(max_length=11)
    father_occupation_choice = (
        ('Agriculture', 'Agriculture'),
        ('Banker', 'Banker'),
        ('Business', 'Business'),
        ('Doctor', 'Doctor'),
        ('Farmer', 'Farmer'),
        ('Fisherman', 'Fisherman'),
        ('Public Service', 'Public Service'),
        ('Private Service', 'Private Service'),
        ('Shopkeeper', 'Shopkeeper'),
        ('Driver', 'Driver'),
        ('Worker', 'Worker'),
        ('N/A', 'N/A'),
    )
    father_occupation = models.CharField(choices=father_occupation_choice, max_length=45)
    father_yearly_income = models.CharField(max_length=20)
    mother_name = models.CharField(max_length=100)
    mother_phone_no = models.CharField(max_length=11)
    mother_occupation_choice = (
        ('Agriculture', 'Agriculture'),
        ('Banker', 'Banker'),
        ('Business', 'Business'),
        ('Doctor', 'Doctor'),
        ('Farmer', 'Farmer'),
        ('Fisherman', 'Fisherman'),
        ('Public Service', 'Public Service'),
        ('Private Service', 'Private Service'),
        ('Shopkeeper', 'Shopkeeper'),
        ('Driver', 'Driver'),
        ('Worker', 'Worker'),
        ('N/A', 'N/A'),
    )
    mother_occupation = models.CharField(choices=mother_occupation_choice, max_length=45)
    guardian_name = models.CharField(max_length=100)
    guardian_phone_no = models.CharField(max_length=11)
    guardian_email = models.EmailField(blank=True, null=True)
    relationship_choice = (
        ('Teacher', 'Teacher'),
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Other','Other')
    )
    relationship_with_student = models.CharField(choices=relationship_choice, max_length=45)

    def __str__(self):
        return self.guardian_name

class EmergencyContactDetails(models.Model):
    emergency_guardian_name = models.CharField(max_length=100)
    address = models.TextField()
    relationship_choice = (
        ('Teacher', 'Teacher'),
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),\
        ('Other','Other')
    )
    relationship_with_student = models.CharField(choices=relationship_choice, max_length=45)
    phone_no = models.CharField(max_length=11)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.emergency_guardian_name

from django.db import models

class PreviousAcademicInfo(models.Model):
    # Existing fields
    institute_name = models.CharField(max_length=100)
    name_of_exam = models.CharField(max_length=100)
    group = models.CharField(max_length=45)
    gpa = models.CharField(max_length=10)
    board_roll = models.IntegerField()
    passing_year = models.IntegerField()

    # New fields for SSC
    ssc_board_name = models.CharField(max_length=100, null=True, blank=True)
    ssc_passing_year = models.IntegerField(null=True, blank=True)
    ssc_seat_no = models.CharField(max_length=50, null=True, blank=True)
    ssc_maths_percentage = models.FloatField(null=True, blank=True)
    ssc_total_percentage = models.FloatField(null=True, blank=True)

    # New fields for HSC
    qualifying_exam_name = models.CharField(max_length=100, null=True, blank=True)
    hsc_board_name = models.CharField(max_length=100, null=True, blank=True)
    hsc_passing_year = models.IntegerField(null=True, blank=True)
    hsc_seat_no = models.CharField(max_length=50, null=True, blank=True)
    hsc_phy_percentage = models.FloatField(null=True, blank=True)
    hsc_chem_percentage = models.FloatField(null=True, blank=True)
    hsc_math_percentage = models.FloatField(null=True, blank=True)
    hsc_additional_eligibility_subject_name = models.CharField(max_length=100, null=True, blank=True)
    hsc_subject_percentage_of_additional = models.FloatField(null=True, blank=True)
    hsc_english_percentage = models.FloatField(null=True, blank=True)
    hsc_total_percentage = models.FloatField(null=True, blank=True)

    # Eligibility
    eligibility_percentage = models.FloatField(null=True, blank=True)

    # CET and JEE fields
    cet_roll_no = models.CharField(max_length=50, null=True, blank=True)
    cet_percentage = models.FloatField(null=True, blank=True)
    jee_application_no = models.CharField(max_length=50, null=True, blank=True)
    jee_percentage = models.FloatField(null=True, blank=True)

    # Home University
    home_university = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.institute_name

class PreviousAcademicCertificate(models.Model):
    birth_certificate = models.FileField(upload_to='documents/', blank=True)
    release_letter = models.FileField(upload_to='documents/', blank=True)
    testimonial = models.FileField(upload_to='documents/', blank=True)
    marksheet = models.FileField(upload_to='documents/', blank=True)
    stipen_certificate = models.FileField(upload_to='documents/', blank=True)
    other_certificate = models.FileField(upload_to='documents/', blank=True)

class AcademicInfo(models.Model):
    class_info = models.ForeignKey(ClassInfo, on_delete=models.CASCADE)
    session_info = models.ForeignKey(Session, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey(GuideTeacher, on_delete=models.CASCADE)
    administration = models.ForeignKey(Designation, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    registration_no = models.IntegerField(unique=True, default=random.randint(100000, 999999))
    department_info = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    # Defining choices for status field
    status_select = (
        ('not enroll', 'Not Enroll'),
        ('enrolled', 'Enrolled'),
        ('regular', 'Regular'),
        ('irregular', 'Irregular'),
        ('passed', 'Passed'),
    )
    status = models.CharField(choices=status_select, default='not enroll', max_length=15)

    # Adding stay_mode and traveling_mode with default None (nullable) or a default value
    stay_mode_choices = (
        ('hostel', 'Hostel'),
        ('private room', 'Private Room'),
        ('local', 'Local'),
    )
    stay_mode = models.CharField(
        max_length=50, 
        choices=stay_mode_choices, 
        null=True,  
        blank=True, 
        default=None  
    )

    traveling_mode_choices = (
        ('college bus', 'College Bus'),
        ('private', 'Private'),
    )
    traveling_mode = models.CharField(
        max_length=50, 
        choices=traveling_mode_choices, 
        null=True,  
        blank=True,  
        default=None  
    )

    # Add the college_bus_stop field, which should only be relevant if traveling_mode is "College Bus"
    college_bus_stop = models.CharField(max_length=100, null=True, blank=True, default=None)

    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, null=True)
    address_info = models.ForeignKey(StudentAddressInfo, on_delete=models.CASCADE, null=True)
    guardian_info = models.ForeignKey(GuardianInfo, on_delete=models.CASCADE, null=True)
    emergency_contact_info = models.ForeignKey(EmergencyContactDetails, on_delete=models.CASCADE, null=True)
    previous_academic_info = models.ForeignKey(PreviousAcademicInfo, on_delete=models.CASCADE, null=True)
    previous_academic_certificate = models.ForeignKey(PreviousAcademicCertificate, on_delete=models.CASCADE, null=True)

    date = models.DateField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically fill the class_info and session_info based on UserProfile if not set
        if not self.class_info or not self.session_info:
            try:
                # Fetch the user profile
                user_profile = self.userprofile
                if user_profile.is_student:  
                    self.class_info = user_profile.student_class  
                    self.session_info = user_profile.student_session  
            except UserProfile.DoesNotExist:
                pass  

        # Call the parent class's save method
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.registration_no)

        
class EnrolledStudent(models.Model):
    class_name = models.ForeignKey(ClassRegistration, on_delete=models.CASCADE)
    student = models.OneToOneField(AcademicInfo, on_delete=models.CASCADE)
    roll = models.IntegerField()
    session_year = models.ForeignKey(Session, default=1, on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['class_name', 'session_year','roll']
    
    def __str__(self):
        personal_info_name = self.student.personal_info.name if self.student.personal_info else "Unknown"
        return f"{personal_info_name} enrolled in {self.class_name} for {self.session_year}"
