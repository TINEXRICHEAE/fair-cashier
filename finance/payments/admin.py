from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Points, Transactions, Users
from .payment_processor import process_payment
import random


class UsersAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('email', 'role', 'is_active', 'is_staff',
                    'is_superuser', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('email', 'role')

    # Default ordering
    ordering = ('email',)

    # Remove filter_horizontal for 'groups' and 'user_permissions'
    filter_horizontal = ()

    # Remove list_filter for 'groups'
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')

    # Define fieldsets for the add/edit user page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Define add_fieldsets for the create user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    # Override the save_model method to set default permissions, role, and generate user_id
    def save_model(self, request, obj, form, change):
        if not change:  # Only during creation
            # Generate a unique user_id if not provided
            if not obj.user_id:
                obj.user_id = Users.objects.generate_user_id()

            # Set is_staff and is_superuser based on the role
            if obj.role == 'admin':
                obj.is_staff = True
                obj.is_superuser = False
            elif obj.role == 'superadmin':
                obj.is_staff = True
                obj.is_superuser = True
            else:
                obj.is_staff = False
                obj.is_superuser = False

            # Set is_active to True by default
            obj.is_active = True

        # Save the user first
        super().save_model(request, obj, form, change)

        # Assign all permissions for Users, Points, and Transactions if the role is 'admin' or 'superadmin'
        if not change and (obj.role == 'admin' or obj.role == 'superadmin'):
            models = [Users, Points, Transactions]
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(
                    content_type=content_type)
                obj.user_permissions.add(*permissions)

    # Custom admin actions (send_points and receive_points) remain unchanged
    def send_points(self, request, queryset):
        for user in queryset:
            if user.role == 'end_user':
                # Simulate receiving cash (integrate with payment API here)
                cash_received = True  # Replace with actual payment API logic
                payment_channel = 'MTN'  # Example: Use MTN Mobile Money
                phone_number = '1234567890'  # Example: End user's phone number
                amount = 100  # Example: Amount in USD
                cash_received = process_payment(
                    amount, phone_number, payment_channel, 'receive')
                if cash_received:
                    points, created = Points.objects.get_or_create(
                        user_id=user.user_id)
                    points.points_balance += 100  # Example: Add 100 points
                    points.points_earned += 100
                    points.save()

                    # Record the transaction
                    Transactions.objects.create(
                        sender_id=request.user.user_id,  # Admin's user_id
                        receiver_id=user.user_id,
                        transaction_type='buy_points',
                        amount=100,  # Number of points
                        payment_channel='MTN Mobile Money',  # Example payment channel
                        status='completed'
                    )

        self.message_user(
            request, f"Points sent to {queryset.count()} end_users.")

    send_points.short_description = "Send points to selected end_users"

    def receive_points(self, request, queryset):
        for user in queryset:
            if user.role == 'end_user':
                points = Points.objects.get(user_id=user.user_id)
                if points.points_balance >= 100:  # Example: Deduct 100 points
                    points.points_balance -= 100
                    points.points_used += 100
                    points.save()

                    # Simulate sending cash (integrate with payment API here)
                    cash_sent = True  # Replace with actual payment API logic
                    payment_channel = 'Visa'  # Example: Use Visa
                    card_details = '4111111111111111'  # Example: End user's card details
                    amount = 100  # Example: Amount in USD
                    cash_sent = process_payment(
                        amount, card_details, payment_channel, 'send')
                    if cash_sent:
                        # Record the transaction
                        Transactions.objects.create(
                            sender_id=request.user.user_id,  # Admin's user_id
                            receiver_id=user.user_id,
                            transaction_type='sell_points',
                            amount=100,  # Number of points
                            payment_channel='Visa',  # Example payment channel
                            status='completed'
                        )

        self.message_user(
            request, f"Points received from {queryset.count()} end_users.")

    receive_points.short_description = "Receive points from selected end_users"


# Register your models here.
admin.site.register(Points)        # Registering Points model
admin.site.register(Transactions)   # Registering Transactions model
# Registering Users model with custom admin class
admin.site.register(Users, UsersAdmin)
