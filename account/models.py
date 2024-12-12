from django.db import models
from django.contrib.auth.models import User
from administration.models import Designation

from academic.models import ClassInfo, ClassRegistration,Session,GuideTeacher, Department
def get_first_image_in_admin():
    admin_dir = os.path.join(settings.MEDIA_ROOT, 'admin/')
    if os.path.exists(admin_dir):
        for file in os.listdir(admin_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                return f'admin/{file}'
    return 'img/default.png' 


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=45)
    photo = models.ImageField(upload_to='admin/', default=get_first_image_in_admin)
    password = models.CharField(max_length=255,default="Mipashya@123") 
    date_of_birth = models.DateField(null=True, blank=True) 

    gender_select = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    gender = models.CharField(choices=gender_select, max_length=6)
    
    employee_select = (
        ('admin', 'Admin'),
        ('professor', 'Professor'),
        ('teacher', 'Teacher'),
        ('register', 'Register'),
        ('student', 'Student'),
        ('employee','employee'),
    )
    employee_type = models.CharField(choices=employee_select, max_length=15,default="student")

    student_class = models.ForeignKey(ClassInfo, null=True, blank=True, on_delete=models.CASCADE)  
    student_session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.CASCADE) 
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE) 
    is_complete = models.BooleanField(default=False)

    def is_complete(self):
        required_fields = [self.student_class, self.student_session, self.department]
        return all(required_fields)

    def __str__(self):
        return self.name


class Message(models.Model):
    # Link the sender and recipient directly to the User model
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_sent_messages'  # Unique related name
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_received_messages'  # Unique related name
    )

    # Message details
    message_text = models.TextField()
    image = models.ImageField(upload_to="message_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"
