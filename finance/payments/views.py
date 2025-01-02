from django.db.models import Q  # Import the Q object
from .models import Transactions
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Points, Users, Transactions
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

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard.html')


def mainAppDemo(request):
    return render(request, 'mainAppDemo.html')


def register_user(request):
    if request.method == 'POST':
        # Extract email and password from the request
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f'Registration Email: {email}')
        print(f'Registration Password: {password}')

        # Validate input
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # Check if the email is already registered
        if Users.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        # Create the user using UsersManager
        user = Users.objects.create_user(
            email=email,
            password=password,  # Password will be hashed automatically
            role='end_user',  # Default role
            is_staff=False,  # Default to non-staff  # Default to non-superuser
        )

        # Return success response
        return JsonResponse({
            'message': 'User registered successfully',
            'user_id': user.user_id,
            'email': user.email,
            'role': user.role
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
            points = Points.objects.get(user_id=request.user.user_id)
        except Points.DoesNotExist:
            # Create a new Points record with an initial balance of 1000
            points = Points.objects.create(
                user_id=request.user.user_id,
                points_balance=1000,
                points_earned=0,
                points_used=0
            )

        # Return the points data
        return JsonResponse({
            'user_id': points.user_id,
            'points_balance': points.points_balance,
            'points_earned': points.points_earned,
            'points_used': points.points_used,
            'created_at': points.created_at,
            'updated_at': points.updated_at
        })

    elif request.method == 'POST':
        # Update the points data for the logged-in user
        try:
            points = Points.objects.get(user_id=request.user.user_id)
        except Points.DoesNotExist:
            # Create a new Points record with an initial balance of 1000
            points = Points.objects.create(
                user_id=request.user.user_id,
                points_balance=1000,
                points_earned=0,
                points_used=0
            )

        # Get the updated values from the request
        points_earned = int(request.POST.get('points_earned', 0))
        points_used = int(request.POST.get('points_used', 0))

        # Update the points data
        points.points_earned += points_earned
        points.points_used += points_used
        points.points_balance = 1000 + points.points_earned - points.points_used
        points.save()

        # Return the updated points data
        return JsonResponse({
            'user_id': points.user_id,
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
            # convert points to amount
            amount = points_to_buy / 128

            # Process payment using payment_processor
            response = process_payment(
                amount, payment_details, payment_channel, 'buy_points', request
            )

            if response.status_code == 200:
                # Update points_balance and points_earned
                points, created = Points.objects.get_or_create(
                    user_id=request.user.user_id
                )
                points.points_balance += points_to_buy
                points.save()

                # Record the transaction
                Transactions.objects.create(
                    sender_id=request.user.user_id,
                    receiver_id=request.user.user_id,
                    transaction_type='buy_points',
                    points=points_to_buy,
                    payment_channel=payment_channel,
                    status='completed'
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
            # convert points to amount
            amount = points_to_sell / 128

            # Check if the user has enough points
            points = get_object_or_404(Points, user_id=request.user.user_id)
            if points.points_balance >= points_to_sell:
                # Simulate sending cash to the user
                response = process_payment(
                    amount, payment_details, payment_channel, 'sell_points', request
                )

                if response.status_code == 200:
                    # Update points_balance and points_used
                    points.points_balance -= points_to_sell
                    points.save()

                    # Record the transaction
                    Transactions.objects.create(
                        sender_id=request.user.user_id,
                        receiver_id=request.user.user_id,
                        transaction_type='sell_points',
                        points=points_to_sell,
                        payment_channel=payment_channel,
                        status='completed'
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
            # Parse the request body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            receiver_email = data.get('receiverEmail')
            points_to_share = int(data.get('pointsToShare'))

            # Authenticate the user
            user = authenticate(username=email, password=password)
            if not user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid email or password.'
                }, status=400)

            # Proceed with the transaction if authentication is successful
            sender_points = get_object_or_404(
                Points, user_id=request.user.user_id)
            receiver = get_object_or_404(Users, email=receiver_email)
            receiver_points, created = Points.objects.get_or_create(
                user_id=receiver.user_id
            )

            if sender_points.points_balance >= points_to_share:
                # Update sender's points
                sender_points.points_balance -= points_to_share
                sender_points.save()

                # Update receiver's points
                receiver_points.points_balance += points_to_share
                receiver_points.save()

                # Record the transaction
                Transactions.objects.create(
                    sender_id=request.user.user_id,
                    receiver_id=receiver.user_id,
                    transaction_type='share_points',
                    points=points_to_share,
                    payment_channel='Internal Transfer',
                    status='completed'
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
            # Fetch all transactions where the user is either the sender or receiver
            transactions = Transactions.objects.filter(
                Q(sender_id=str(request.user.user_id)) | Q(
                    receiver_id=str(request.user.user_id))
            ).order_by('-created_at')

            # Serialize the transactions
            transaction_list = []
            for transaction in transactions:
                if transaction.transaction_type == 'buy_points':
                    # For buy_points, the user is always the receiver
                    direction = 'Received'
                elif transaction.transaction_type == 'sell_points':
                    # For sell_points, the user is always the sender
                    direction = 'Sent'
                elif transaction.transaction_type == 'share_points':
                    # For share_points, determine direction based on sender_id and receiver_id
                    if str(transaction.sender_id) == str(request.user.user_id):
                        direction = 'Sent'
                    else:
                        direction = 'Received'
                else:
                    # Default to 'Unknown' for unsupported transaction types
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
def get_user_email(request):
    if request.method == 'GET':
        try:
            logger.info(f"Fetching email for user: {request.user}")
            return JsonResponse({
                'status': 'success',
                'email': request.user.email
            })
        except Exception as e:
            logger.error(f"Error fetching user email: {str(e)}")
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
