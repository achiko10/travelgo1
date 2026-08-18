from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_password_reset_email(email, pin):
    """Celery background task to send password reset PIN via email."""
    try:
        send_mail(
            "Travel Go - პაროლის აღდგენა",
            f"პაროლის აღდგენის კოდი: {pin}\nკოდი 30 წუთის განმავლობაში მოქმედებს.",
            'support@travelgo.ge',
            [email],
            fail_silently=True
        )
        return True
    except Exception:
        return False
