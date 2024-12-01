from django.utils.html import format_html
from django.contrib import admin
from .models import (
    PersonalInfo, StudentAddressInfo, GuardianInfo, 
    EmergencyContactDetails, PreviousAcademicInfo, 
    PreviousAcademicCertificate, AcademicInfo, EnrolledStudent
)
from account.models import UserProfile


class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['get_userprofile', 'name', 'phone_no', 'email', 'gender', 'blood_group', 'date_of_birth', 'display_photo']
    search_fields = ['name', 'userprofile__user__username']
    list_filter = ['blood_group', 'gender']

    def get_userprofile(self, obj):
        return obj.userprofile
    get_userprofile.short_description = 'User Profile'

    def display_photo(self, obj):
        """
        Custom method to display the photo as a rounded thumbnail and clickable to view full size.
        """
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />'
                '</a>',
                obj.photo.url,  # Full-size image URL
                obj.photo.url,  # Thumbnail image URL
            )
        return "No Photo"
    display_photo.short_description = "Photo"


class StudentAddressInfoAdmin(admin.ModelAdmin):
    list_display = ('district', 'upazilla', 'union', 'village')
    search_fields = ['village']
    list_filter = ['district']


class GuardianInfoAdmin(admin.ModelAdmin):
    list_display = ['get_userprofile', 'father_name', 'mother_name', 'guardian_name', 'relationship_with_student']
    search_fields = ['guardian_name', 'father_name', 'mother_name']
    list_filter = ['relationship_with_student']

    def get_userprofile(self, obj):
        related_academic_info = AcademicInfo.objects.filter(guardian_info=obj).first()
        return related_academic_info.userprofile if related_academic_info else "N/A"
    get_userprofile.short_description = 'User Profile'


class EmergencyContactDetailsAdmin(admin.ModelAdmin):
    list_display = ['get_userprofile', 'emergency_guardian_name', 'relationship_with_student', 'phone_no']
    search_fields = ['emergency_guardian_name', 'phone_no']
    list_filter = ['relationship_with_student']

    def get_userprofile(self, obj):
        related_academic_info = AcademicInfo.objects.filter(emergency_contact_info=obj).first()
        return related_academic_info.userprofile if related_academic_info else "N/A"
    get_userprofile.short_description = 'User Profile'


class PreviousAcademicInfoAdmin(admin.ModelAdmin):
    list_display = ['get_userprofile', 'institute_name', 'name_of_exam', 'group', 'gpa', 'passing_year']
    search_fields = ['institute_name', 'name_of_exam']
    list_filter = ['passing_year']

    def get_userprofile(self, obj):
        related_academic_info = AcademicInfo.objects.filter(previous_academic_info=obj).first()
        return related_academic_info.userprofile if related_academic_info else "N/A"
    get_userprofile.short_description = 'User Profile'


class AcademicInfoAdmin(admin.ModelAdmin):
    list_display = [
        'get_userprofile', 'registration_no', 'class_info', 'session_info', 
        'status', 'date', 'is_delete'
    ]
    search_fields = ['registration_no', 'userprofile__user__username']
    list_filter = ['status', 'class_info', 'session_info']

    def get_userprofile(self, obj):
        return obj.userprofile
    get_userprofile.short_description = 'User Profile'


class EnrolledStudentAdmin(admin.ModelAdmin):
    list_display = ['get_userprofile', 'class_name','session_year', 'roll', 'date']
    search_fields = ['roll', 'student__userprofile__user__username']
    list_filter = ['class_name']

    def get_userprofile(self, obj):
        return obj.student.userprofile
    get_userprofile.short_description = 'User Profile'


# Registering all models with their customized admin classes
admin.site.register(PersonalInfo, PersonalInfoAdmin)
admin.site.register(StudentAddressInfo, StudentAddressInfoAdmin)
admin.site.register(GuardianInfo, GuardianInfoAdmin)
admin.site.register(EmergencyContactDetails, EmergencyContactDetailsAdmin)
admin.site.register(PreviousAcademicInfo, PreviousAcademicInfoAdmin)
admin.site.register(PreviousAcademicCertificate)  # No custom admin class needed
admin.site.register(AcademicInfo, AcademicInfoAdmin)
admin.site.register(EnrolledStudent, EnrolledStudentAdmin)
