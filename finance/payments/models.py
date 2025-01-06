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


class UsersManager(BaseUserManager):
    def generate_user_id(self):
        """Generate a unique 16-digit user_id."""
        while True:
            user_id = random.randint(1000000000000000, 9999999999999999)
            if not Users.objects.filter(user_id=user_id).exists():
                return user_id

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        # Generate a unique user_id if not provided
        if 'user_id' not in extra_fields:
            extra_fields['user_id'] = self.generate_user_id()

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

        # Assign the user to the appropriate group
        if user.role == 'admin':
            # Assign to the 'Admins' group with the superadmin as the admin
            superadmin = Users.objects.filter(role='superadmin').first()
            if superadmin:
                group, created = Group.objects.get_or_create(
                    name='Admins',
                    superadmin=superadmin
                )
                user.group = group
                user.save()
        elif user.role == 'end_user':
            # Assign to the 'End-users' group with the superadmin as the admin
            superadmin = Users.objects.filter(role='superadmin').first()
            if superadmin:
                group, created = Group.objects.get_or_create(
                    name='End-users',
                    superadmin=superadmin
                )
                user.group = group
                user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Set the default role for superusers to 'superadmin'
        if 'role' not in extra_fields:
            extra_fields['role'] = 'superadmin'

        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigIntegerField(primary_key=True)
    email = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=128)
    ROLE_CHOICES = (
        ('end_user', 'End User'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    admin_email = models.EmailField(
        max_length=50, blank=True, null=True)  # New field for end_user
    group = models.ForeignKey(
        'Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
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
        return f"User(id={self.user_id}, email={self.email}, role={self.role})"

    # Add these methods for Django's admin and permissions
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


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
