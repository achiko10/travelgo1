from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_password_reset_email(email, pin):
    """ Phase 2: Asynchronous password reset email sending via Celery """
    subject = "Travel Go - პაროლის აღდგენა"
    message = f"თქვენი პაროლის აღდგენის უსაფრთხოების კოდია (PIN): {pin}\nკოდი აქტიურია 10 წუთის განმავლობაში. არ გააზიაროთ ეს კოდი!"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@travelgo.ge')
    try:
        send_mail(subject, message, from_email, [email], fail_silently=False)
        return f"Email sent to {email}"
    except Exception as e:
        return f"Failed to send email: {e}"
