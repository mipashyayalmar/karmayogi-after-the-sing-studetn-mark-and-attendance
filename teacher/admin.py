from django.utils.html import format_html
from django.contrib import admin
from .models import AddressInfo, EducationInfo, TrainingInfo, JobInfo, ExperienceInfo, PersonalInfo


@admin.register(AddressInfo)
class AddressInfoAdmin(admin.ModelAdmin):
    list_display = ('userprofile', 'district', 'upazilla', 'union', 'village')  # Specify the fields to display
    list_filter = ('district', 'upazilla', 'union')  # Add filters for better admin management
    search_fields = ('userprofile__name', 'village')  # Enable search functionality


@admin.register(EducationInfo)
class EducationInfoAdmin(admin.ModelAdmin):
    list_display = ('name_of_exam', 'institute', 'group', 'grade', 'board', 'passing_year')
    search_fields = ('name_of_exam', 'institute')


@admin.register(TrainingInfo)
class TrainingInfoAdmin(admin.ModelAdmin):
    list_display = ('training_name', 'year', 'duration', 'place')
    search_fields = ('training_name', 'place')


@admin.register(JobInfo)
class JobInfoAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'joning_date',
        'institute_name',
        'job_designation',
        'department',
        'scale',
        'grade_of_post',
        'first_time_scale_due_year',
        'second_time_scale_due_year',
        'promotion_due_year',
        'recreation_leave_due_year',
        'expected_retirement_year',
    )
    list_filter = ('category', 'job_designation', 'department')
    search_fields = ('institute_name',)


@admin.register(ExperienceInfo)
class ExperienceInfoAdmin(admin.ModelAdmin):
    list_display = ('institute_name', 'designation', 'trainer')
    search_fields = ('institute_name', 'designation')


@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'employee_type',
        'administration',
        'display_photo',
        'date_of_birth',
        'email',
        'date',
    )
    list_filter = ('employee_type', 'gender', 'religion', 'nationality', 'marital_status')
    search_fields = ('name', 'phone_no', 'email', 'nid', 'e_tin')

    def display_photo(self, obj):
        """
        Custom method to display the photo as a rounded image and clickable to view full size.
        """
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />'
                '</a>',
                obj.photo.url,  # Full-size image URL for the link
                obj.photo.url,  # Thumbnail image URL for the <img> tag
            )
        return "No Photo"

    display_photo.short_description = "Photo"  # This will display as the column header in the admin
