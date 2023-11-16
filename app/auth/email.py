import os
from flask_mail import Message
from app.extensions import mail
from flask import current_app, render_template


def send_email(to,
               subject,
               template,
               attachments=None,
               ctx=None,
               async_mail=True):

    if ctx is None:
        ctx = {}

    msg = Message(subject, recipients=[to])
    msg.body = _try_renderer_template(template, ext="txt", **ctx)
    msg.html = _try_renderer_template(template, ext="html", **ctx)

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if async_mail:
        # celery task
        pass
    else:
        mail.send(msg)


def _try_renderer_template(template_path, ext="txt", **kwargs):
    try:
        return render_template("{0}.{1}".format(template_path, ext), **kwargs)
    except IOError:
        pass
        # log error
