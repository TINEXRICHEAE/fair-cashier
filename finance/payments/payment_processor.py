from django.utils import timezone
from django.http import JsonResponse
from .models import Users


def process_payment(amount, payment_details, payment_channel, transaction_type, request):
    try:
        # Determine the admin reference (superadmin for all roles)
        superadmin = Users.objects.filter(role='superadmin').first()
        if not superadmin:
            return JsonResponse({
                'status': 'error',
                'message': 'Superadmin not found.'
            }, status=400)

        admin_reference = superadmin.email

        # Process payment based on the payment channel
        if payment_channel == 'MTN':
            return process_mtn_mobile_money_payment(amount, payment_details, transaction_type, admin_reference)
        elif payment_channel == 'Airtel':
            return process_airtel_mobile_money_payment(amount, payment_details, transaction_type, admin_reference)
        elif payment_channel == 'Bank':
            return process_bank_transfer_payment(amount, payment_details, transaction_type, admin_reference)
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


def process_mtn_mobile_money_payment(amount, phone_number, transaction_type, admin_reference):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'Sell Points':
        message = {
            'status': 'success',
            'message': 'MTN Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': phone_number,
                'From': admin_reference,
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
                'To': admin_reference,
                'Time': timestamp
            }
        }
    return JsonResponse(message)


def process_airtel_mobile_money_payment(amount, phone_number, transaction_type, admin_reference):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'Sell Points':
        message = {
            'status': 'success',
            'message': 'Airtel Mobile Money Payment Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': phone_number,
                'From': admin_reference,
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
                'To': admin_reference,
                'Time': timestamp
            }
        }
    return JsonResponse(message)


def process_bank_transfer_payment(amount, account_number, transaction_type, admin_reference):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if transaction_type == 'Sell Points':
        message = {
            'status': 'success',
            'message': 'Bank Transfer Successful',
            'details': {
                'Transaction': 'Sell Points',
                'Payment': f'${amount:.2f} (UGX {amount * 3500:.2f})',
                'To': account_number,
                'From': admin_reference,
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
                'To': admin_reference,
                'Time': timestamp
            }
        }
    return JsonResponse(message)
