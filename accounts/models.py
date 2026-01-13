# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model for Tuition SMS.

    - Keeps is_teacher / is_student flags for your existing logic.
    - Adds a role field (admin / staff) for permission decisions.
    """
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_STAFF, 'Card Mark Staff'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)

    # Existing flags you already had
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    # Helper properties for easy checks
    @property
    def is_admin(self):
        # Superuser overrides role (superuser always treated as admin)
        return self.is_superuser or (self.role == self.ROLE_ADMIN)

    @property
    def is_staff_user(self):
        # staff_user means the role is staff OR admin (admins implicitly staff)
        return self.role == self.ROLE_STAFF or self.is_admin
