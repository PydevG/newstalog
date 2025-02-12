from django.shortcuts import render
from django_daraja.mpesa.core import MpesaClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def get_access_token(request):
    mpesa = MpesaClient()
    token = mpesa.access_token()
    return JsonResponse({"access_token": token})

def stk_push(request):
    phone_number = "254708374149"  # Change to your test number
    amount = 10  # Amount to charge
    account_reference = "Test Payment"
    transaction_desc = "Payment for Django-Daraja Test"

    mpesa = MpesaClient()
    callback_url = "https://yourdomain.com/mpesa/stk-callback/"
    response = mpesa.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url=callback_url)

    
    return JsonResponse(response)


def simulate_c2b_payment(request):
    mpesa = MpesaClient()
    shortcode = "600998"  # Sandbox Paybill
    phone_number = "254708374149"
    amount = 100
    bill_ref_number = "Test123"

    response = mpesa.c2b_payment(shortcode, phone_number, amount, bill_ref_number)
    return JsonResponse(response)

@csrf_exempt
def stk_push_callback(request):
    data = json.loads(request.body)
    print("STK Callback Received: ", data)  # Debugging
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})

