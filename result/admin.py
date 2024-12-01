from django.contrib import admin
from .models import SubjectRegistration

class SubjectRegistrationAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'select_class', 'session_info', 'marks', 'pass_mark')
    search_fields = ('subject_name',)
    list_filter = ('select_class', 'session_info')

admin.site.register(SubjectRegistration, SubjectRegistrationAdmin)