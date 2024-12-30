from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Points(models.Model):
    points_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=16)
    points_balance = models.IntegerField(blank=True, null=True)
    points_earned = models.IntegerField(blank=True, null=True)
    points_used = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # {{ edit_1 }}
    updated_at = models.DateTimeField(auto_now=True)  # {{ edit_2 }}

    class Meta:
        managed = True  # {{ edit_3 }}
        db_table = 'points'

    def __str__(self):  # {{ edit_4 }}
        # {{ edit_5 }
        return f"Points(user_id={self.user_id}, balance={self.points_balance})"


class Transactions(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    sender_id = models.CharField(max_length=16)
    receiver_id = models.CharField(max_length=16)
    transaction_type = models.CharField(max_length=50)
    amount = models.IntegerField()
    payment_channel = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'transactions'

    def __str__(self):
        # {{ edit_10 }}
        return f"Transaction(id={self.transaction_id}, amount={self.amount}, status={self.status})"


class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser):
    user_id = models.BigIntegerField(primary_key=True)
    email = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add these fields for Django's admin and authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # Add any other required fields here

    class Meta:
        managed = True
        db_table = 'users'

    def __str__(self):
        return f"User(id={self.user_id}, email={self.email}, role={self.role})"

    # Add these methods for Django's admin and permissions
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
