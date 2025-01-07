from django.contrib.auth.models import Group as BuiltInGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Points, Transactions, Users, Group


class GroupAdmin(BaseGroupAdmin):
    # Add your custom fields to the admin interface
    list_display = ('name', 'admin', 'superadmin')
    search_fields = ('name', 'admin__email', 'superadmin__email')
    # Ensure permissions are displayed properly
    filter_horizontal = ('permissions',)


# Register your custom Group model
admin.site.register(Group, GroupAdmin)
# Unregister the built-in Group model
admin.site.unregister(BuiltInGroup)


@admin.register(Users)
class UsersAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('email', 'role', 'admin_email', 'is_active',
                    'is_staff', 'is_superuser', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('email', 'role', 'admin_email')

    # Default ordering
    ordering = ('email',)

    # Remove filter_horizontal for 'groups' and 'user_permissions'
    filter_horizontal = ('user_permissions', 'groups')

    # List filters
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')

    # Define fieldsets for the add/edit user page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
         'fields': ('role', 'admin_email', 'groups')}),
        ('Permissions', {'fields': ('is_active',
         'is_staff', 'is_superuser', 'user_permissions')}),
    )

    # Define add_fieldsets for the create user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'admin_email', 'groups', 'user_permissions'),

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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            # form.base_fields['email'].disabled = True
            form.base_fields['role'].disabled = True
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True
        return form


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    list_display = ("points_balance", )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['points_balance'].disabled = True
        return form


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ("transaction_type", )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['transaction_type'].disabled = True
        return form


