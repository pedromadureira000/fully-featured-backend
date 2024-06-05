from django.core.mail import EmailMultiAlternatives
from fully_featured.settings import BASE_URL, FROM_EMAIL
from django.contrib.gis.geoip2 import GeoIP2


def send_reset_user_password_email(email, auth_token, country):
    url =  f"{BASE_URL}/reset_password/{auth_token}"
    subject = "Redefir senha" if country == "BR" else "Reset password"
    body = f"Clique para resetar a senha: {url}" if country == "BR" else f"Click to reset your password: {url}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        to=[email],
    )

    html = f'<p>Redefina sua senha clicando nesse link {url}</p>' if country == "BR" else f'<p>Reset you password by clicking on this link {url}</p>'
    msg.attach_alternative(html, "text/html")
    msg.send()

def user_is_blocked(user):
    if user.subscription_status == 2:
        return "trial_ended"
    elif user.subscription_status == 4:
        return "subscription_unpaid"
    elif user.subscription_status == 5:
        return "subscription_canceled"

def get_client_ip(request):
    # Check if the request was forwarded by a proxy
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Fallback to REMOTE_ADDR if HTTP_X_FORWARDED_FOR is not present
        ip = request.META.get('REMOTE_ADDR')
    #  print('========================> ip: ',ip )
    return ip

def get_country_code_from_ip(ip):
    g = GeoIP2()
    try:
        return g.country(ip)["country_code"]
    except Exception as err:
        #  print('========================> err: ',err )
        #  TODO log or something
        return "XX"
