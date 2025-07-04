# Generated by Django 4.2.2 on 2024-11-10 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("academic", "__first__"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=45)),
                ("photo", models.ImageField(upload_to="admin/")),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[("male", "Male"), ("female", "Female")], max_length=6
                    ),
                ),
                (
                    "employee_type",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("professor", "Professor"),
                            ("teacher", "Teacher"),
                            ("register", "Register"),
                            ("student", "Student"),
                            ("peon", "Peon"),
                        ],
                        max_length=15,
                    ),
                ),
                (
                    "class_info",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="academic.classinfo",
                    ),
                ),
                (
                    "session_info",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="academic.session",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
