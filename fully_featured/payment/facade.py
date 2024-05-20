from django.core.mail import EmailMultiAlternatives
from fully_featured.settings import BASE_URL, FROM_EMAIL, STRIPE_PAYMENT_LINK


def send_subscription_success_email(user, lang):
    email = user.email
    subject = "Bem-vindo ao Mind-Organizer! Sua assinatura está confirmada 🎉" if lang == "pt" else "Welcome to Mind-Organizer! Your Subscription is Confirmed 🎉"
    auth_token = user.auth_token.key
    body = _get_subscription_success_email_html_body(user, lang, auth_token, reset_pass=False)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(body, "text/html")
    msg.send()

def send_account_created_email_with_change_password_link(user, lang):
    email = user.email
    auth_token = user.auth_token.key
    subject = "Bem-vindo ao Mind-Organizer! Sua assinatura está confirmada 🎉" if lang == "pt" else "Welcome to Mind-Organizer! Your Subscription is Confirmed 🎉"
    body = _get_subscription_success_email_html_body(user, lang, auth_token, reset_pass=True)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(body, "text/html")
    msg.send()

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
            <p>Contacte-nos em <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> ou pelo WhatsApp em <a href="https://wa.link /ouz6vl">https://wa.link/ouz6vl</a></p>
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
            <p>Contact us at <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> or on WhatsApp at <a href="https://wa.link /ouz6vl"> https://wa.link/ouz6vl</a></p>
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

def send_subscription_canceled_email_due_to_unpaid_bill(user, lang):
    email = user.email
    user_name = user.name
    subject = "Cancelamento da Inscrição por Falta de Pagamento" if lang == "pt" else "Subscription Canceled Due to Unpaid Bill"
    stripe_payment_link = STRIPE_PAYMENT_LINK
    
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
            <p>Notamos que houve um problema com o pagamento de sua assinatura da <strong>Mind-Organizer</strong>, e sua inscrição foi cancelada. Se houver algo que possamos fazer para ajudar com a questão do pagamento, por favor, nos avise.</p>
            <p>Se resolver a questão do pagamento e desejar reativar sua inscrição, estamos sempre aqui para recebê-lo de volta.</p>
            <p>Para tentar novamente o pagamento, clique no link abaixo:</p>
            <p><a href="{stripe_payment_link}" style="color: #1a73e8;">Tentar novamente o pagamento</a></p>
            <p>Contacte-nos em <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> ou pelo WhatsApp em <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a></p>
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
            <p>We've noticed there was an issue with your payment for the <strong>Mind-Organizer</strong> subscription, and your subscription has been canceled. If there's anything we can do to help with the payment issue, please let us know.</p>
            <p>If you resolve the payment issue and wish to reactivate your subscription, we'll always be here to welcome you back.</p>
            <p>To retry your payment, click the link below:</p>
            <p><a href="{stripe_payment_link}" style="color: #1a73e8;">Retry Payment</a></p>
            <p>Contact us at <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> or on WhatsApp at <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a></p>
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

def send_payment_failed_email(user, lang):
    email = user.email
    user_name = user.name
    stripe_payment_link = STRIPE_PAYMENT_LINK
    subject = "Falha no Pagamento da Inscrição" if lang == "pt" else "Subscription Payment Failed"
    
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
            <p>Houve um problema com o pagamento de sua inscrição na <strong>Mind-Organizer</strong>. Por favor, verifique suas informações de pagamento e tente novamente.</p>
            <p>Para tentar novamente, clique no link abaixo:</p>
            <p><a href="{stripe_payment_link}" style="color: #1a73e8;">Tentar Pagamento</a></p>
            <p>Se precisar de ajuda ou tiver alguma dúvida, estou disponível pelo email <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> ou pelo WhatsApp <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a>. Fique à vontade para entrar em contato a qualquer momento.</p>
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
            <p>There was an issue with your subscription payment for <strong>Mind-Organizer</strong>. Please check your payment details and try again.</p>
            <p>To retry your payment, click the link below:</p>
            <p><a href="{stripe_payment_link}" style="color: #1a73e8;">Retry Payment</a></p>
            <p>If you ever need help or have questions, I’m just an email away at <a href="mailto:contact@petersoftwarehouse.com">contact@petersoftwarehouse.com</a> or on WhatsApp at <a href="https://wa.link/ouz6vl">https://wa.link/ouz6vl</a>. Feel free to reach out anytime.</p>
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
