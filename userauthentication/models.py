from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Head Master', 'HEAD_MASTER'),
        ('Admin', 'ADMIN'),
        ('Teacher', 'TEACHER'),
        ('Staff', 'STAFF'),
    ]

    name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)


    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'role',]

    objects = UserManager()

    def __str__(self):
        return self.username
