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

        # Generate a unique 16-character user_id
        def generate_user_id():
            # Generate a 16-digit integer
            return random.randint(1000000000000000, 9999999999999999)

        user_id = generate_user_id()
        while Users.objects.filter(user_id=user_id).exists():
            user_id = generate_user_id()  # Regenerate if the user_id already exists

        # Create the user using UsersManager
        user = Users.objects.create_user(
            user_id=user_id,
            email=email,
            password=password,  # Password will be hashed automatically
            role='end_user',  # Default role
            is_active=True,  # Ensure the user is active
            is_staff=False,  # Default to non-staff
            is_superuser=False  # Default to non-superuser
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
