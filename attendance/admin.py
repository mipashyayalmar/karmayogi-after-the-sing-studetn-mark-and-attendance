from django.contrib import admin
from .models import StudentAttendance, StudentMark

class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'select_class', 'subject', 'status', 'date', 'timestamp')
    search_fields = ('student__roll', 'select_class__name')
    list_filter = ('status', 'date')

class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'mark_type', 'score', 'exam_date')
    search_fields = ('student__roll', 'subject__name')
    list_filter = ('exam_date', 'mark_type')

admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(StudentMark, StudentMarkAdmin)
