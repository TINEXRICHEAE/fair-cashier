from django.db.models import Q  # Import the Q object
from .models import Transactions
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Points, Users, Transactions, Group
from django.shortcuts import get_object_or_404
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .payment_processor import process_payment
from .models import Users, Points, Transactions
from .models import Points, Users
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password
from .models import Users
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import string
import random
from django.shortcuts import render


def dashboard(request):
    return render(request, 'dashboard.html')


def mainAppDemo(request):
    return render(request, 'mainAppDemo.html')


def register_user(request):
    if request.method == 'POST':
        # Extract email, password, and role from the request
        email = request.POST.get('email')
        password = request.POST.get('password')
        register_as_admin = request.POST.get(
            'register_as_admin') == 'on'  # Check if checkbox is checked
        role = 'admin' if register_as_admin else 'end_user'  # Set role based on checkbox

        # Validate input
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # Check if the email is already registered
        if Users.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        # Create the user using UsersManager
        user = Users.objects.create_user(
            email=email,
            password=password,
            role=role,
            is_staff=(role == 'admin' or role == 'superadmin'),
            is_superuser=(role == 'superadmin'),
        )

        # Assign the user to the appropriate group
        if role == 'admin':
            # Assign to the 'Admins' group with the superadmin as the admin
            superadmin = Users.objects.filter(role='superadmin').first()
            if not superadmin:
                return JsonResponse({'error': 'Superadmin not found'}, status=400)
            group, created = Group.objects.get_or_create(
                name='Admins',
                superadmin=superadmin
            )
            user.group = group
            user.save()
        elif role == 'end_user':
            # Assign to the 'End-users' group with the superadmin as the admin
            superadmin = Users.objects.filter(role='superadmin').first()
            if not superadmin:
                return JsonResponse({'error': 'Superadmin not found'}, status=400)
            group, created = Group.objects.get_or_create(
                name='End-users',  # New group for end_users
                superadmin=superadmin
            )
            user.group = group
            user.save()

        # Return success response
        return JsonResponse({
            'message': 'User registered successfully',
            'user_id': user.user_id,
            'email': user.email,
            'role': user.role,
            'group': user.group.name if user.group else None
        }, status=201)

    return render(request, 'register_user.html')


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f'Login Email: {email}')
        print(f'Login Password: {password}')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            print(f'Session after login: {request.session.items()}')
            print(f'User authenticated: {request.user.is_authenticated}')
            return JsonResponse({
                'message': 'Login successful',
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

    return render(request, 'login_user.html')


logger = logging.getLogger(__name__)


def check_auth(request):
    logger.info(f"User authenticated: {request.user.is_authenticated}")
    return JsonResponse({'is_authenticated': request.user.is_authenticated})


def logout_user(request):
    if request.method == 'POST':
        logout(request)  # Ends the user's session
        return JsonResponse({'message': 'Logout successful'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def points_view(request):
    if request.method == 'GET':
        # Fetch the points data for the logged-in user
        try:
            points = Points.objects.get(
                user_id=request.user)  # Use the Users instance
        except Points.DoesNotExist:
            # Create a new Points record with an initial balance of 1000
            points = Points.objects.create(
                user_id=request.user,  # Use the Users instance
                points_balance=1000,
                points_earned=0,
                points_used=0
            )

        # Return the points data
        return JsonResponse({
            'user_id': points.user_id.user_id,  # Access the user_id from the Users instance
            'points_balance': points.points_balance,
            'points_earned': points.points_earned,
            'points_used': points.points_used,
            'created_at': points.created_at,
            'updated_at': points.updated_at
        })

    elif request.method == 'POST':
        # Update the points data for the logged-in user
        try:
            points = Points.objects.get(
                user_id=request.user)  # Use the Users instance
        except Points.DoesNotExist:
            # Create a new Points record with an initial balance of 1000
            points = Points.objects.create(
                user_id=request.user,  # Use the Users instance
                points_balance=1000,
                points_earned=0,
                points_used=0
            )

        # Only process points_earned and points_used for end users
        if request.user.role == 'end_user':
            # Get the updated values from the request
            points_earned = int(request.POST.get('points_earned', 0))
            points_used = int(request.POST.get('points_used', 0))

            # Deduct points_earned from the linked admin's balance
            linked_admin = Users.objects.filter(
                email=request.user.admin_email, role='admin').first()
            if not linked_admin:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Linked admin not found.'
                }, status=400)

            try:
                linked_admin_points = Points.objects.get(
                    user_id=linked_admin)  # Use the Users instance
            except Points.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Linked admin does not have a points record.'
                }, status=400)

            # Check if the linked admin has enough points before deducting
            if linked_admin_points.points_balance < points_earned:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Linked admin does not have enough points.'
                }, status=400)

            # Check if the user has enough points for the operation
            if points.points_balance < points_used:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Insufficient points balance for the operation.'
                }, status=400)

            # Deduct points_earned from the linked admin's balance
            linked_admin_points.points_balance -= points_earned
            linked_admin_points.points_used += points_earned

            # Add points_used to the linked admin's balance
            linked_admin_points.points_balance += points_used
            linked_admin_points.points_earned += points_used
            linked_admin_points.save()

            # Update the user's points
            points.points_earned += points_earned
            points.points_used += points_used
            points.points_balance = 1000 + points.points_earned - points.points_used
            points.save()

        else:
            # For non-end users (admins or superadmins), return their current points data
            return JsonResponse({
                'user_id': points.user_id.user_id,  # Access the user_id from the Users instance
                'points_balance': points.points_balance,
                'points_earned': points.points_earned,
                'points_used': points.points_used,
                'created_at': points.created_at,
                'updated_at': points.updated_at
            })

        # Return the updated points data for end users
        return JsonResponse({
            'user_id': points.user_id.user_id,  # Access the user_id from the Users instance
            'points_balance': points.points_balance,
            'points_earned': points.points_earned,
            'points_used': points.points_used,
            'created_at': points.created_at,
            'updated_at': points.updated_at
        })

    else:
        # Handle unsupported HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def buy_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            points_to_buy = int(data.get('pointsToBuy'))
            payment_channel = data.get('payment_channel')
            payment_details = data.get('payment_details')
            email = data.get('email')
            password = data.get('password')

            # Authenticate the user
            user = authenticate(username=email, password=password)
            if not user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid email or password.'
                }, status=400)

            amount = points_to_buy / 128

            response = process_payment(
                amount, payment_details, payment_channel, 'Buy Points', request
            )

            if response.status_code == 200:
                points, created = Points.objects.get_or_create(
                    user_id=request.user.user_id
                )
                points.points_balance += points_to_buy
                points.save()

                superadmin = Users.objects.filter(role='superadmin').first()
                if not superadmin:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Superadmin not found.'
                    }, status=400)

                Transactions.objects.create(
                    sender=superadmin,
                    receiver=request.user,
                    transaction_type='Buy Points',
                    points=points_to_buy,
                    payment_channel=payment_channel,
                    status='Completed'
                )

                return response
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Payment failed. Please try again.'
                }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)


@login_required
def sell_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            points_to_sell = int(data.get('pointsToSell'))
            payment_channel = data.get('payment_channel')
            payment_details = data.get('payment_details')
            email = data.get('email')
            password = data.get('password')

            # Authenticate the user
            user = authenticate(username=email, password=password)
            if not user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid email or password.'
                }, status=400)

            amount = points_to_sell / 128

            points = get_object_or_404(Points, user_id=request.user.user_id)
            if points.points_balance >= points_to_sell:
                response = process_payment(
                    amount, payment_details, payment_channel, 'Sell Points', request
                )

                if response.status_code == 200:
                    points.points_balance -= points_to_sell
                    points.save()

                    superadmin = Users.objects.filter(
                        role='superadmin').first()
                    if not superadmin:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Superadmin not found.'
                        }, status=400)

                    Transactions.objects.create(
                        sender=request.user,
                        receiver=superadmin,
                        transaction_type='Sell Points',
                        points=points_to_sell,
                        payment_channel=payment_channel,
                        status='Completed'
                    )

                    return response
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Payment failed. Please try again.'
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Insufficient points balance.'
                }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)


@login_required
def share_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            receiver_email = data.get('receiverEmail')
            points_to_share = int(data.get('pointsToShare'))

            # Re-authenticate the user
            user = authenticate(username=email, password=password)
            if not user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid email or password.'
                }, status=400)

            # Find the user (sender)
            sender_points = get_object_or_404(
                Points, user_id=request.user.user_id)
            # Check if the user has enough points
            if sender_points.points_balance >= points_to_share:
                # Find the recipient
                receiver = get_object_or_404(Users, email=receiver_email)
                if not receiver:
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Recipient {receiver_email} not found."
                    }, status=404)
                # Update sender's points
                sender_points.points_balance -= points_to_share
                sender_points.save()

                # Update recipient's points
                receiver_points, created = Points.objects.get_or_create(
                    user_id=receiver.user_id
                )
                receiver_points.points_balance += points_to_share
                receiver_points.save()

                # Record the transaction
                Transactions.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    transaction_type='Share Points',
                    points=points_to_share,
                    payment_channel='Internal',
                    status='Completed'
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Points shared successfully.',
                    'details': {
                        'Transaction': 'Share Points',
                        'From': request.user.email,
                        'To': receiver.email,
                        'Points': points_to_share,
                        'Time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Insufficient points balance.'
                }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)


@login_required
def transaction_history(request):
    if request.method == 'GET':
        try:
            transactions = Transactions.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
            ).order_by('-created_at')

            transaction_list = []
            for transaction in transactions:
                if transaction.transaction_type == 'Buy Points':
                    direction = 'Received'
                elif transaction.transaction_type == 'Sell Points':
                    direction = 'Sent'
                elif transaction.transaction_type == 'Share Points':
                    if transaction.sender == request.user:
                        direction = 'Sent'
                    else:
                        direction = 'Received'
                else:
                    direction = 'Unknown'

                transaction_list.append({
                    'date': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': transaction.transaction_type,
                    'points': transaction.points,
                    'status': transaction.status,
                    'direction': direction
                })

            return JsonResponse({
                'status': 'success',
                'transactions': transaction_list
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)


logger = logging.getLogger(__name__)


@login_required
def user_profile(request):
    if request.method == 'GET':
        try:
            # Fetch the user's email and admin email
            user_email = request.user.email
            admin_email = request.user.admin_email if request.user.role == 'end_user' else None

            return JsonResponse({
                'status': 'success',
                'email': user_email,
                'admin_email': admin_email
            })
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    elif request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            admin_email = data.get('admin_email')

            # Validate admin email
            if not admin_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Admin email is required.'
                }, status=400)

            # Ensure the user is an end_user
            if request.user.role != 'end_user':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Only end users can update their admin email.'
                }, status=403)

            # Update the admin_email field
            request.user.admin_email = admin_email
            request.user.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Admin email updated successfully.'
            })
        except Exception as e:
            logger.error(f"Error updating admin email: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)


@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            # Delete the user account
            user = request.user
            user.delete()

            # Logout the user
            logout(request)

            return JsonResponse({
                'status': 'success',
                'message': 'Account deleted successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)
