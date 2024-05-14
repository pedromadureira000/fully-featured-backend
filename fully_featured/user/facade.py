from django.core.mail import EmailMultiAlternatives
from fully_featured.settings import BASE_URL, FROM_EMAIL


def send_reset_user_password_email(email, auth_token, lang):
    url =  f"{BASE_URL}/reset_password/{auth_token}"
    subject = "Redefir senha" if lang == "pt" else "Reset password"
    body = f"Clique para resetar a senha: {url}" if lang == "pt" else f"Click to reset your password: {url}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    html = f'<p>Redefina sua senha clicando nesse link {url}</p>' if lang == "pt" else f'<p>Reset you password by clicking on this link {url}</p>'
    msg.attach_alternative(html, "text/html")
    msg.send()
