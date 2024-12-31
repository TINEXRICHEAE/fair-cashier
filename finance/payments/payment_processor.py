import requests


def process_payment(amount, payment_details, payment_channel, transaction_type):
    """
    Process payment using the specified payment channel.

    Args:
        amount (float): The amount to be paid.
        payment_details (str): The phone number or card details for the payment.
        payment_channel (str): The payment channel ('MTN', 'Airtel', or 'Visa').
        transaction_type (str): The transaction type ('send' or 'receive').

    Returns:
        bool: True if the payment is successful, False otherwise.
    """
    if payment_channel == 'MTN':
        return process_mtn_mobile_money_payment(amount, payment_details, transaction_type)
    elif payment_channel == 'Airtel':
        return process_airtel_mobile_money_payment(amount, payment_details, transaction_type)
    elif payment_channel == 'Visa':
        return process_visa_payment(amount, payment_details, transaction_type)
    else:
        raise ValueError(f"Unsupported payment channel: {payment_channel}")


def process_mtn_mobile_money_payment(amount, phone_number, transaction_type):
    """
    Process payment using MTN Mobile Money API.

    Args:
        amount (float): The amount to be paid.
        phone_number (str): The phone number for the payment.
        transaction_type (str): The transaction type ('send' or 'receive').

    Returns:
        bool: True if the payment is successful, False otherwise.
    """
    url = 'https://api.mtn.com/v1/payments'
    headers = {
        'Authorization': 'Bearer YOUR_MTN_API_KEY',
        'Content-Type': 'application/json'
    }
    payload = {
        'amount': amount,
        'phone_number': phone_number,
        'currency': 'USD',
        'transaction_type': transaction_type  # Explicitly define the payment direction
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200


def process_airtel_mobile_money_payment(amount, phone_number, transaction_type):
    """
    Process payment using Airtel Mobile Money API.

    Args:
        amount (float): The amount to be paid.
        phone_number (str): The phone number for the payment.
        transaction_type (str): The transaction type ('send' or 'receive').

    Returns:
        bool: True if the payment is successful, False otherwise.
    """
    url = 'https://api.airtel.com/v1/payments'
    headers = {
        'Authorization': 'Bearer YOUR_AIRTEL_API_KEY',
        'Content-Type': 'application/json'
    }
    payload = {
        'amount': amount,
        'phone_number': phone_number,
        'currency': 'USD',
        'transaction_type': transaction_type  # Explicitly define the payment direction
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200


def process_visa_payment(amount, card_details, transaction_type):
    """
    Process payment using Visa API.

    Args:
        amount (float): The amount to be paid.
        card_details (str): The card details for the payment.
        transaction_type (str): The transaction type ('send' or 'receive').

    Returns:
        bool: True if the payment is successful, False otherwise.
    """
    url = 'https://api.visa.com/v1/payments'
    headers = {
        'Authorization': 'Bearer YOUR_VISA_API_KEY',
        'Content-Type': 'application/json'
    }
    payload = {
        'amount': amount,
        'card_details': card_details,
        'currency': 'USD',
        'transaction_type': transaction_type  # Explicitly define the payment direction
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200
