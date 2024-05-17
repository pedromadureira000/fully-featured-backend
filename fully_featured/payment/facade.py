from django.core.mail import EmailMultiAlternatives
from fully_featured.settings import BASE_URL, FROM_EMAIL


def send_subscription_success_email(user, lang):
    email = user.email
    subject = _get_subscription_success_email_subject(lang)
    auth_token = user.auth_token.key
    body = _get_subscription_success_email_body(user, lang, auth_token, reset_pass=False)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    html = _get_subscription_success_email_html_body(user, lang, auth_token, reset_pass=False)

    msg.attach_alternative(html, "text/html")
    msg.send()

def send_account_created_email_with_change_password_link(user, lang):
    email = user.email
    auth_token = user.auth_token.key
    subject = _get_subscription_success_email_subject(lang)
    body = _get_subscription_success_email_body(user, lang, auth_token, reset_pass=True)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    html = _get_subscription_success_email_html_body(user, lang, auth_token, reset_pass=True)
    msg.attach_alternative(html, "text/html")
    msg.send()

def send_subscription_canceled_email(user, lang):
    email = user.email
    user_name = user.name
    subject = "Cancelamento da Inscrição" if lang == "pt" else "Subscription Canceled"
    
    if lang == "pt":
        body = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Olá {user_name},</p>
            <p>Lamentamos saber que você cancelou sua inscrição na <strong>Mind-Organizer</strong>. Se houver algo que possamos fazer para melhorar sua experiência, por favor, nos avise.</p>
            <p>Se você mudar de ideia, estamos sempre aqui para recebê-lo de volta.</p>
            <p>Atenciosamente,</p>
            <p>Pedro Madureira<br>
            Fundador, Mind-Organizer</p>
        </body>
        </html>
        """
    else:
        body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {user_name},</p>
            <p>We're sorry to see you go. Your subscription to <strong>Mind-Organizer</strong> has been canceled. If there's anything we can do to improve your experience, please let us know.</p>
            <p>If you change your mind, we'll always be here to welcome you back.</p>
            <p>Best regards,</p>
            <p>Peter Henry<br>
            Founder, Mind-Organizer</p>
        </body>
        </html>
        """
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(body, "text/html")
    msg.send()

def _get_subscription_success_email_subject(lang):
    subject = "Bem-vindo ao Mind-Organizer! Sua assinatura está confirmada 🎉" if lang == "pt" else "Welcome to Mind-Organizer! Your Subscription is Confirmed 🎉"
    return subject

def _get_subscription_success_email_body(user, lang, auth_token, reset_pass):
    if reset_pass:
        reset_password_url =  f"{BASE_URL}/reset_password/{auth_token}"
        access_platform_txt_call = f"Clique para definir a senha: {reset_password_url}" if lang == "pt" else f"Click to define your password: {reset_password_url}"
    else:
        access_platform_txt_call = "Acesse sua conta em https://app.petersoftwarehouse.com/" if lang == "pt" else "Access your account at https://app.petersoftwarehouse.com/"

    if lang == "pt":
        body = f"""Olá {user.name},
            Sou Pedro Madureira, o fundador da Mind-Organizer, e gostaria de agradecer pessoalmente por se inscrever!

            {access_platform_txt_call}

            Se precisar de ajuda ou tiver alguma dúvida, estou disponível pelo email contact@petersoftwarehouse.com ou pelo WhatsApp https://wa.link/ouz6vl. Fique à vontade para entrar em contato a qualquer momento.

            Redes Sociais:
            * https://www.instagram.com/petersoftwarehouse/

            Mais uma vez, obrigado por se juntar à Mind-Organizer. Estou muito animado em ter você conosco e mal posso esperar para ouvir seu feedback!!

            Abraços,

            Peter Henry
            Fundador, Mind-Organizer
            """
    else:
        body = f"""Hi {user.name},
        I’m Peter Henry, the founder of Mind-Organizer, and I just wanted to personally say thanks for subscribing!

        {access_platform_txt_call}

        If you ever need help or have questions, I’m just an email away at contact@petersoftwarehouse.com or on whatsapp https://wa.link/ouz6vl. Feel free to reach out anytime.


        Social Media:
        * https://www.instagram.com/petersoftwarehouse/

        Thanks again for joining Mind-Organizer. I’m really excited to have you with us and can't wait to hear your feedback!!

        Cheers,

        Peter
        Founder, Mind-Organizer
        """
    return body

def _get_subscription_success_email_html_body(user, lang, auth_token, reset_pass):
    reset_password_url =  f"{BASE_URL}/reset_password/{auth_token}"
    if reset_pass:
        access_platform_txt_call = f'<p>Clique para definir sua senha <a href="{reset_password_url}">{reset_password_url}</a></p>' if lang == "pt" else f'<p>Click to set your password <a href="{reset_password_url}">{reset_password_url}</a></p>'
 
    else:
        access_platform_txt_call = '<p>Acesse sua conta em <a href="https://app.petersoftwarehouse.com/">https://app.petersoftwarehouse.com/</a></p>' if lang == "pt" else 'Access your account at <a href="https://app.petersoftwarehouse.com/">https://app.petersoftwarehouse.com/</a></p>'

    if lang == "pt":
        html = f"""<p>Olá {user.name}</p>
        <p>Sou Pedro Madureira, o fundador da <strong>Mind-Organizer</strong>, e gostaria de agradecer pessoalmente por se inscrever!</p>
        {access_platform_txt_call}
        <p>Se precisar de ajuda ou tiver alguma dúvida, estou disponível pelo email <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> ou pelo WhatsApp <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a>. Fique à vontade para entrar em contato a qualquer momento.</p>
        <p>Redes Sociais:</p>
        <ul>
            <li><a href="https://www.instagram.com/petersoftwarehouse/">Instagram</a></li>
        </ul>
        <p>Mais uma vez, obrigado por se juntar à <strong>Mind-Organizer</strong>. Estou muito animado em ter você conosco e mal posso esperar para ouvir seu feedback!!</p>
        <p>Abraços,</p>
        <p>Pedro Madureira<br>
        Fundador, Mind-Organizer</p>
        """
    else:
        html = f"""<p>Hi {user.name},</p> 
        <p>I’m Peter Henry, the founder of <strong>Mind-Organizer</strong>, and I just wanted to personally say thanks for subscribing!</p>
        {access_platform_txt_call}
        <p>If you ever need help or have questions, I’m just an email away at <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> or on WhatsApp at <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a>. Feel free to reach out anytime.</p>
        <p>Social Media:</p>
        <ul>
            <li><a href="https://www.instagram.com/petersoftwarehouse/">Instagram</a></li>
        </ul>
        <p>Thanks again for joining <strong>Mind-Organizer</strong>. I’m really excited to have you with us and can't wait to hear your feedback!!</p>
        <p>Cheers,</p>
        <p>Peter<br>
        Founder, Mind-Organizer</p>
        """
    return html
