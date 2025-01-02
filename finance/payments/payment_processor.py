import requests

from django.contrib.auth import authenticate
from django.utils import timezone
from django.http import JsonResponse
import json


def process_payment(amount, payment_details, payment_channel, transaction_type, request):
    try:
        # Parse the request body for re-authentication
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(username=email, password=password)
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email or password.'
            }, status=400)

        # Process payment based on the payment channel
        if payment_channel == 'MTN':
            return process_mtn_mobile_money_payment(amount, payment_details, transaction_type)
        elif payment_channel == 'Airtel':
            return process_airtel_mobile_money_payment(amount, payment_details, transaction_type)
        elif payment_channel == 'bank_transfer':
            return process_bank_transfer_payment(amount, payment_details, transaction_type)
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Unsupported payment channel: {payment_channel}'
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def process_mtn_mobile_money_payment(amount, phone_number, transaction_type):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'sell_points':
        message = {
            'status': 'success',
            'message': 'MTN Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': phone_number,
                'From': 'ADMIN123',
                'Time': timestamp
            }
        }
    else:
        message = {
            'status': 'success',
            'message': 'MTN Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Buy Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'From': phone_number,
                'To': 'ADMIN123',
                'Time': timestamp
            }
        }
    return JsonResponse(message)


def process_airtel_mobile_money_payment(amount, phone_number, transaction_type):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'sell_points':
        message = {
            'status': 'success',
            'message': 'Airtel Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': phone_number,
                'From': 'ADMIN123',
                'Time': timestamp
            }
        }
    else:
        message = {
            'status': 'success',
            'message': 'Airtel Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Buy Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'From': phone_number,
                'To': 'ADMIN123',
                'Time': timestamp
            }
        }
    return JsonResponse(message)


def process_bank_transfer_payment(amount, account_number, transaction_type):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'sell_points':
        message = {
            'status': 'success',
            'message': 'Bank Transfer Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': account_number,
                'From': 'ADMIN123',
                'Time': timestamp
            }
        }
    else:
        message = {
            'status': 'success',
            'message': 'Bank Transfer Successful',
            'details': {
                'Transaction': 'Buy Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'From': account_number,
                'To': 'ADMIN123',
                'Time': timestamp
            }
        }
    return JsonResponse(message)
