from django.core.mail import EmailMultiAlternatives
from fully_featured.settings import BASE_URL


def send_reset_user_password_email(email, auth_token):
    url =  f"{BASE_URL}/reset_password/{auth_token}"
    msg = EmailMultiAlternatives(
        subject="Reset password",
        body=f"Click to reset your password: {url}",
        from_email="Mailgun Sandbox <postmaster@sandboxa3124ed5bfe242c69aec66978f252bf2.mailgun.org>",
        to=[email],
    )

    html = f'<p>Reset you passoword by clicking on this link {url}</p>' 
    msg.attach_alternative(html, "text/html")
    msg.send()
