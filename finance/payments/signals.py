from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import Users, Group


@receiver(post_save, sender=Users)
def assign_user_to_group(sender, instance, created, **kwargs):
    if created:  # Only trigger for new users
        if instance.role == 'admin':
            # Assign to the 'Admins' group
            superadmin = Users.objects.filter(role='superadmin').first()
            if superadmin:
                # Create or get the 'Admins' group
                group, created = Group.objects.get_or_create(
                    name='Admins',
                    superadmin=superadmin  # Set the superadmin for the group
                )
                # Add the user to the 'Admins' group
                instance.groups.add(group)

                # Assign permissions 24, 28, 32, 36 to the 'Admins' group
                permissions = Permission.objects.filter(
                    id__in=[24, 28, 32, 36])
                group.permissions.add(*permissions)

        elif instance.role == 'end_user':
            # Assign to the 'End-users' group
            superadmin = Users.objects.filter(role='superadmin').first()
            if superadmin:
                group, created = Group.objects.get_or_create(
                    name='End-users',
                    superadmin=superadmin  # Set the superadmin for the group
                )
                instance.groups.add(group)
