from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.validators import math
#  from anymail.message import attach_inline_image_file
from fully_featured.settings import BASE_URL, FROM_EMAIL
from django.db.models import F


def send_account_confirmation_email(email, auth_token, lang):
    activate_url =  f"{BASE_URL}/activate_account/{auth_token}"
    subject = "Por favor, ative sua conta" if lang == "pt" else "Please, activate your account"
    body = f"Clique para ativar sua conta: {activate_url}" if lang == "pt" else f"Click to activate your account: {activate_url}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email = FROM_EMAIL,
        to=[email],
    )
    #  logo_cid = attach_inline_image_file(msg, "/path/to/logo.jpg")
    #  html = """<img alt="Logo" src="cid:{logo_cid}">
              #  <p>Please <a href="https://example.com/activate">activate</a>
              #  your account</p>""".format(logo_cid=logo_cid)
    html = f'<p>Ative sua conta clicando neste link {activate_url}</p>' if lang == "pt" else f'<p>Please activate your account by clicking on this link {activate_url}</p>' 
    # TODO fix the html link block. useh ssl and my own domain
    #  html = f'<p><b>Please</b> <a href="{activate_url}">activate</a>your account</p>'
    msg.attach_alternative(html, "text/html")
    msg.send()

def get_paginated_results(user, startingIndex, model, serializer, sort_by, **kwargs):
    startingIndex = int(startingIndex) if startingIndex and startingIndex.isdigit() else 0
    items_per_page = 20
    start = startingIndex
    end = startingIndex + items_per_page

    queryset = model.objects.filter(user_id=user.id, **kwargs).order_by(sort_by)

    totalRecords = queryset.count()
    result = serializer(queryset[start:end], many=True).data

    return {
        "result": result,
        "totalRecords": totalRecords
    }

def get_paginated_tasks_results(user, startingIndex, model, serializer, sort_by, **kwargs):
    startingIndex = int(startingIndex) if startingIndex and startingIndex.isdigit() else 0
    items_per_page = 50
    start = startingIndex
    end = startingIndex + items_per_page

    queryset = model.objects.filter(user_id=user.id, **kwargs).order_by(sort_by)

    totalRecords = queryset.count()
    tasks = queryset[start:end]
    #  status_choices = (
        #  (1, "Postponed"),
        #  (2, "Pendent"),
        #  (3, "Doing"),
        #  (4, "Done"),
    #  )
    result = serializer(tasks, many=True).data
    #  if "status" in kwargs:  XXX ORdering stuff
        #  result = serializer(tasks, many=True).data
    #  else:
        #  order = [3, 2, 1, 4]
        #  order = {key: i for i, key in enumerate(order)}
        #  ordered_tasks = sorted(tasks, key=lambda item: order.get(item.status, 0))
        #  result = serializer(ordered_tasks, many=True).data

    return {
        "result": result,
        "totalRecords": totalRecords
    }

def reorder_group_after_delete(user, model):
    groups = model.objects.filter(user=user).order_by('order')
    index = 0
    if len(groups) > 0:
        for group in groups:
            group.order = index
            index = index + 1
    model.objects.bulk_update(groups, ["order"]);
