from django.utils.html import format_html
from django.contrib import admin
from .models import UserProfile, Message


# Custom filter for Employee Type in UserProfile
class EmployeeTypeFilter(admin.SimpleListFilter):
    title = 'Employee Type' 
    parameter_name = 'employee_type'  

    def lookups(self, request, model_admin):
        """
        Returns a list of filter options. Each option is a tuple of 
        (value, human-readable name).
        """
        return [
            ('student', 'Student'),
            ('employee', 'Employee'),
            ('teacher', 'Teacher'),
        ]

    def queryset(self, request, queryset):
        """
        Filters the queryset based on the selected value.
        """
        if self.value() == 'student':
            return queryset.filter(employee_type='student')
        elif self.value() == 'employee':
            return queryset.filter(employee_type='employee')
        elif self.value() == 'teacher':
            return queryset.filter(employee_type='teacher')
        return queryset


# Admin configuration for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'colored_name',  
        'user', 
        'gender', 
        'colored_employee_type',  
        'student_class', 
        'student_session', 
        'department', 
        'date_of_birth', 
        'display_photo', 
    )
    list_filter = (EmployeeTypeFilter, 'gender', 'student_class', 'student_session', 'department')  # Custom filter
    search_fields = ('name', 'user__username')  # Search by name or username
    ordering = ('name',)  # Order by name

    def get_queryset(self, request):
        """
        Optionally filter the queryset based on the logged-in user type.
        For example, superusers see all profiles, while others may have restricted views.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            # Example filter: restrict to users in the same department (customize as needed)
            return queryset.filter(department=request.user.userprofile.department)

    def display_photo(self, obj):
        """
        Custom method to display the photo as a rounded image and clickable to view full size.
        """
        if obj.photo:
            # Render the photo as a clickable link to the full-size image
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />'
                '</a>',
                obj.photo.url, 
                obj.photo.url,  
            )
        return "No Photo"

    def colored_name(self, obj):
        """
        Display the name with a background color based on the employee type.
        """
        color = self.get_background_color(obj.employee_type)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px; border-radius: 5px;">{}</span>',
            color,
            obj.name,
        )
    colored_name.short_description = 'Name'

    def colored_employee_type(self, obj):
        """
        Display the employee type as a colored badge.
        """
        color = self.get_background_color(obj.employee_type)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px; border-radius: 5px;">{}</span>',
            color,
            obj.employee_type.capitalize(),
        )
    colored_employee_type.short_description = 'Employee Type'

    @staticmethod
    def get_background_color(employee_type):
        """
        Get the background color based on the employee type.
        """
        if employee_type == 'student':
            return '#4CAF50' 
        elif employee_type == 'professor':
            return '#aa21f3' 
        elif employee_type == 'employee':
            return '#2196F3' 
        elif employee_type == 'teacher':
            return '#FF9800' 
        return '#9E9E9E' 


# Admin configuration for Message
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'sender', 
        'recipient', 
        'message_text', 
        'created_at', 
        'is_read',
    )
    list_filter = ('is_read', 'created_at')  # Filter by read status and creation date
    search_fields = ('sender__username', 'recipient__username', 'message_text')  # Search by sender, recipient, or message content
    ordering = ('-created_at',)  # Order by newest messages first

    def get_queryset(self, request):
        """
        Restrict messages based on user type. Superusers see all messages, 
        while others see only their own sent/received messages.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(sender=request.user) | queryset.filter(recipient=request.user)


# Register the models
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MessageAdmin)
