# Import the built-in Group model
from django.contrib.auth.models import Group as BuiltInGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Points, Transactions, Users, Group


class UsersAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('email', 'role', 'admin_email', 'group', 'is_active',
                    'is_staff', 'is_superuser', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('email', 'role', 'admin_email')

    # Default ordering
    ordering = ('email',)

    # Remove filter_horizontal for 'groups' and 'user_permissions'
    filter_horizontal = ('user_permissions', 'groups')

    # List filters
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'group')

    # Define fieldsets for the add/edit user page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
         'fields': ('role', 'admin_email', 'group', 'groups')}),
        ('Permissions', {'fields': ('is_active',
         'is_staff', 'is_superuser', 'user_permissions')}),
    )

    # Define add_fieldsets for the create user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'admin_email', 'group', 'groups', 'user_permissions'),

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
                # Assign the user to the 'Admins' group with the superadmin as the admin
                superadmin = Users.objects.filter(role='superadmin').first()
                if superadmin:
                    group, created = Group.objects.get_or_create(
                        name='Admins',
                        superadmin=superadmin
                    )
                    obj.group = group
            elif obj.role == 'superadmin':
                obj.is_staff = True
                obj.is_superuser = True
                # Superadmin does not belong to any group
                obj.group = None
            else:
                obj.is_staff = False
                obj.is_superuser = False
                # Assign the user to the 'End-users' group with the superadmin as the admin
                superadmin = Users.objects.filter(role='superadmin').first()
                if superadmin:
                    group, created = Group.objects.get_or_create(
                        name='End-users',
                        superadmin=superadmin
                    )
                    obj.group = group

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


admin.site.register(Users, UsersAdmin)
# Register your models here.
admin.site.register(Points)        # Registering Points model
admin.site.register(Transactions)   # Registering Transactions model
# Registering Group model
# Registering Users model with custom admin class


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
