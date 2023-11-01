from datetime import datetime, timedelta
import os
import re
from smtplib import SMTPException
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib import messages
from django.core.mail import send_mail
from modelmssql import queryDBall, queryDBrow, queryDBscalar
import commons


class FormSendmail(forms.Form):
    senderName = forms.CharField(
        label="Sender Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[\w.0-9 -]*$",
                message="invalid characters",
            )
        ],
    )
    senderEmail = forms.EmailField(
        label="From",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        max_length=60,
    )
    recipientEmail = forms.EmailField(
        label="To",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        max_length=60,
    )
    invoiceLink = forms.URLField(
        label="Invoice",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=3,
        max_length=250,
    )
    subject = forms.CharField(
        label="Subject",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=200,
        validators=[
            RegexValidator(
                regex="^[\s\w.0-9@,:/?%'=-]*$",
                message="invalid characters",
            )
        ],
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=1024,
        validators=[
            RegexValidator(
                regex=r"^[\n\r\s\w.0-9@,:/?%'=&-]*$",
                message="invalid characters",
            )
        ],
    )


def index(request):
    loginName = request.session.get("loginName", "")
    default_message = commons.get_standard_email()
    MSGFR = default_message.get("MSGFR", "")
    MSGEN = default_message.get("MSGEN", "")
    MSGEND = default_message.get("MSGEND", "")
    MSGNAME = default_message.get("MSGNAME", "")
    MSGEMAIL = default_message.get("MSGEMAIL", "")
    MSGSUBJECT = default_message.get("MSGSUBJECT", "")

    default_values = dict()
    default_values["message"] = request.POST.get("message") or (MSGFR + MSGEN + MSGEND)
    default_values["senderName"] = request.POST.get("senderName") or MSGNAME
    default_values["senderEmail"] = request.POST.get("senderEmail") or MSGEMAIL
    default_values["subject"] = request.POST.get("subject") or MSGSUBJECT
    default_values["invoiceLink"] = request.POST.get("invoiceLink") or request.GET.get(
        "invoiceLink"
    )
    default_values["recipientEmail"] = request.POST.get(
        "recipientEmail"
    ) or request.GET.get("recipientEmail")
    formSendmail = FormSendmail(default_values)
    isFrozen = False
    if (
        request.method == "POST"
        and request.POST.get("updateItemBTN")
        and formSendmail.is_valid()
    ):
        senderName = formSendmail.cleaned_data.get("senderName")
        senderEmail = formSendmail.cleaned_data.get("senderEmail")
        recipientEmail = formSendmail.cleaned_data.get("recipientEmail")
        subject = formSendmail.cleaned_data.get("subject")
        message = formSendmail.cleaned_data.get("message")
        message += "\n" + formSendmail.cleaned_data.get("invoiceLink")
        sender = f'"{senderName}" <{senderEmail}>'

        try:
            send_mail(
                subject,
                message,
                sender,
                [recipientEmail],
                fail_silently=False,
            )
            messages.add_message(request, messages.SUCCESS, f"Message Sent")
            isFrozen = True
        except SMTPException as e:
            messages.add_message(request, messages.WARNING, f"message was no sent:{e}")

    """ --- """
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSendmail": formSendmail,
        "isFrozen": isFrozen,
    }
    return render(request, "sendmail/sample.html", context)
