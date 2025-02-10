import sib_api_v3_sdk
from django.conf import settings
from sib_api_v3_sdk.rest import ApiException

def send_verification_email(user_email, verification_link):
    """
    Sends an email verification link to the user via Brevo.
    """
    # Configure Brevo API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY

    # Create API instance
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Define sender and recipient
    sender = {"name": "My Website", "email": "no-reply@mywebsite.com"}  # Change this to your sender email
    recipient = [{"email": user_email}]

    # Email content
    subject = "Verify Your Email - My Website"
    html_content = f"""
    <h2>Welcome to My Website!</h2>
    <p>Click the link below to verify your email:</p>
    <a href="{verification_link}" style="display:inline-block;padding:10px 20px;background:#007bff;color:white;text-decoration:none;border-radius:5px;">Verify Email</a>
    <p>If you didn't request this, you can ignore this email.</p>
    """

    # Create the email data
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=recipient,
        subject=subject,
        html_content=html_content,
    )

    try:
        api_instance.send_transac_email(email_data)
        return True  # Email sent successfully
    except ApiException as e:
        print("Error sending verification email:", e)
        return False  # Email sending failed
