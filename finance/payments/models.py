from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import random
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import Group as DjangoGroup


class Group(DjangoGroup):  # Inherit from Django's built-in Group model
    group_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='managed_group',
        limit_choices_to={'role': 'admin'},
        null=True,
        blank=True
    )
    superadmin = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='supervised_groups',
        limit_choices_to={'role': 'superadmin'},
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'groups'

    def __str__(self):
        if self.admin:
            return f"Group(name={self.name}, admin={self.admin.email})"
        elif self.superadmin:
            return f"Group(name={self.name}, superadmin={self.superadmin.email})"
        else:
            return f"Group(name={self.name})"

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        # Set a default role if not provided
        if 'role' not in extra_fields:
            extra_fields['role'] = 'end_user'  # Default role for regular users

        # Set is_staff and is_superuser based on the role
        if extra_fields['role'] == 'admin':
            extra_fields['is_staff'] = True
            extra_fields['is_superuser'] = False
        elif extra_fields['role'] == 'superadmin':
            extra_fields['is_staff'] = True
            extra_fields['is_superuser'] = True
        else:
            extra_fields['is_staff'] = False
            extra_fields['is_superuser'] = False

        # Set is_active to True by default
        extra_fields['is_active'] = True

        # Create the user
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Set the default role for superusers to 'superadmin'
        if 'role' not in extra_fields:
            extra_fields['role'] = 'superadmin'

        return self.create_user(email, password, **extra_fields)

    def create_anonymous_user(self):
        """Create an anonymous user if it doesn't already exist."""
        anonymous_email = "anonymous@example.com"
        if not self.filter(email=anonymous_email).exists():
            anonymous_user = self.create(
                email=anonymous_email,
                role="end_user",
                is_active=False,  # Anonymous users should not be active
                is_staff=False,
                is_superuser=False,
            )
            anonymous_user.set_unusable_password()  # Anonymous users should not have a password
            anonymous_user.save()
            return anonymous_user
        return None


class Users(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=128)
    ROLE_CHOICES = (
        ('end_user', 'End User'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    admin_email = models.EmailField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # Add any other required fields here

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"User(id={self.id}, email={self.email}, role={self.role})"

class Points(models.Model):
    points_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE)
    points_balance = models.IntegerField(blank=True, null=True)
    points_earned = models.IntegerField(blank=True, null=True)
    points_used = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'points'

    def __str__(self):

        return f"Points(user_id={self.user_id}, balance={self.points_balance})"


class Transactions(models.Model):
    # Transaction type choices
    TRANSACTION_TYPE_CHOICES = [
        ('Buy Points', 'Buy Points'),
        ('Sell Points', 'Sell Points'),
        ('Share Points', 'Share Points'),
    ]

    # Payment channel choices
    PAYMENT_CHANNEL_CHOICES = [
        ('MTN', 'MTN'),
        ('Airtel', 'Airtel'),
        ('Bank', 'Bank'),
        ('Internal', 'Internal'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Processing', 'Processing'),
        ('Failed', 'Failed'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        'Users', on_delete=models.CASCADE, related_name='sending_transactions')
    receiver = models.ForeignKey(
        'Users', on_delete=models.CASCADE, related_name='receiving_transactions')
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    payment_channel = models.CharField(
        max_length=50, choices=PAYMENT_CHANNEL_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'transactions'

    def __str__(self):
        return f"Transaction(id={self.transaction_id}, points={self.points}, status={self.status})"
