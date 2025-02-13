from django.core.mail import send_mail
from django.conf import settings

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

