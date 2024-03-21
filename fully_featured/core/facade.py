from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from anymail.message import attach_inline_image_file


def se():
    send_mail("It works!", "This will get sent through Mailgun",
              "Anymail Sender <from@example.com>", ["weekendy8@gmail.com"])



#  msg = EmailMultiAlternatives(
    #  subject="Please activate your account",
    #  body="Click to activate your account: https://example.com/activate",
    #  from_email="Example <admin@example.com>",
    #  to=["New User <user1@example.com>", "account.manager@example.com"],
    #  reply_to=["Helpdesk <support@example.com>"])

#  logo_cid = attach_inline_image_file(msg, "/path/to/logo.jpg")
#  html = """<img alt="Logo" src="cid:{logo_cid}">
          #  <p>Please <a href="https://example.com/activate">activate</a>
          #  your account</p>""".format(logo_cid=logo_cid)
#  msg.attach_alternative(html, "text/html")
#  msg.send()
