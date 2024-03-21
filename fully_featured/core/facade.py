from django.core.mail import EmailMultiAlternatives, EmailMessage
#  from anymail.message import attach_inline_image_file
from fully_featured.settings import BASE_URL


def send_account_confirmation_email__(email, auth_token):
    subject = "Please activate your account"
    from_email = "Mailgun Sandbox <postmaster@sandboxa3124ed5bfe242c69aec66978f252bf2.mailgun.org>"
    to = email
    activate_url =  f"{BASE_URL}/activate_account/{auth_token}"
    html_content = f'<p><b>Please</b> <a href="{activate_url}">activate</a> your account</p>'
    msg = EmailMessage(subject, html_content, from_email, [to])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    #  send_mail("It works!", f"Click to activate your account: {activate_url}",
              #  "Mailgun Sandbox <postmaster@sandboxa3124ed5bfe242c69aec66978f252bf2.mailgun.org>", [email])

def send_account_confirmation_email(email, auth_token):
    activate_url =  f"{BASE_URL}/activate_account/{auth_token}"
    msg = EmailMultiAlternatives(
        subject="Please activate your account",
        body=f"Click to activate your account: {activate_url}",
        from_email="Mailgun Sandbox <postmaster@sandboxa3124ed5bfe242c69aec66978f252bf2.mailgun.org>",
        to=[email],
    )
    #  logo_cid = attach_inline_image_file(msg, "/path/to/logo.jpg")
    #  html = """<img alt="Logo" src="cid:{logo_cid}">
              #  <p>Please <a href="https://example.com/activate">activate</a>
              #  your account</p>""".format(logo_cid=logo_cid)
    html = f'<p>Please activate your account by clicking on this link {activate_url}</p>' 
    # TODO fix the html link block. useh ssl and my own domain
    #  html = f'<p><b>Please</b> <a href="{activate_url}">activate</a>your account</p>'
    msg.attach_alternative(html, "text/html")
    msg.send()
