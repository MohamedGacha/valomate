from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def send_verification_email(email, token):
    verification_link = f"http://{settings.DOMAIN_NAME}{reverse('verify_email', kwargs={'token': token})}"
    subject = "Verify your email"
    message = f"Click the link to verify your email: {verification_link}"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
