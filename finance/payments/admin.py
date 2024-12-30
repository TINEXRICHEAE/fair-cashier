from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Points, Transactions, Users


class UsersAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('email', 'role', 'is_staff', 'is_superuser')

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
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )


# Register your models here.
admin.site.register(Points)        # Registering Points model
admin.site.register(Transactions)   # Registering Transactions model
# Registering Users model with custom admin class
admin.site.register(Users, UsersAdmin)
