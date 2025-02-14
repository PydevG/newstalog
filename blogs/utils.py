from django.core.mail import send_mail
from django.conf import settings
import requests

def send_verification_email(user_email, verification_link):
    """
    Sends an email verification link to the user via Zoho Mail SMTP.
    """
    subject = "Verify Your Email - Stalog"
    html_content = f"""
    <h2>Welcome to Stalog!</h2>
    <p>Click the link below to verify your email:</p>
    <a href="{verification_link}" style="display:inline-block;padding:10px 20px;background:#007bff;color:white;text-decoration:none;border-radius:5px;">Verify Email</a>
    <p>If you didn't request this, you can ignore this email.</p>
    """

    # Send email using Zoho SMTP
    email_sent = send_mail(
        subject=subject,
        message="",  # Django requires a plain text version, but we only use HTML here
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_content,  # Send HTML content
        fail_silently=False,  # Set to False for debugging
    )

    return email_sent > 0  # Returns True if at least one email was sent



def get_pesapal_token():
    url = "https://pay.pesapal.com/v3/api/Auth/RequestToken"
    
    headers = {"Content-Type": "application/json"}
    
    data = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        print("Pesapal Token Response:", response_data)  # Debugging

        if response.status_code == 200 and "token" in response_data:
            return response_data["token"]
        else:
            return None
    except Exception as e:
        print("Error fetching Pesapal token:", e)
        return None