from django.db import models
from django.db.models.deletion import CASCADE
from academic.models import ClassRegistration
from student.models import EnrolledStudent
from result.models import SubjectRegistration
from django.utils import timezone

class AttendanceManager(models.Manager):
    def create_attendance(self, std_class, std_roll, subject, attendance_date, status):
        std_cls = ClassRegistration.objects.get(name=std_class)
        students = EnrolledStudent.objects.filter(roll=std_roll, class_name=std_cls)

        if not students.exists():
            raise ValueError("No student found with the given roll number.")
        elif students.count() > 1:
            raise ValueError("Multiple students found with the same roll number in this class.")

        std = students.first()
        return StudentAttendance.objects.create(
            select_class=std_cls,
            student=std,
            subject=subject,
            status=status,
            date=attendance_date,
            timestamp=timezone.now()
        )

class StudentAttendance(models.Model):
    STATUS_CHOICES = (
        (0, 'Absent'),
        (1, 'Present'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    date = models.DateField()
    select_class = models.ForeignKey(ClassRegistration, on_delete=CASCADE, null=True)
    student = models.ForeignKey(EnrolledStudent, on_delete=CASCADE)
    subject = models.ForeignKey(SubjectRegistration, on_delete=CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('student', 'date', 'timestamp'),)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Unknown')

from django.db import models
from django.db.models import CASCADE

class StudentMark(models.Model): 
    student = models.ForeignKey(EnrolledStudent, on_delete=CASCADE)
    subject = models.ForeignKey(SubjectRegistration, on_delete=CASCADE)
    exam_date = models.DateField()
    mark_type = models.CharField(max_length=100)  
    score = models.FloatField()
    updated_date = models.DateTimeField(auto_now=True)
    total_score = models.IntegerField(null=True, blank=True)  

    class Meta:
        unique_together = (('student', 'subject', 'exam_date', 'mark_type'),)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.mark_type}"
