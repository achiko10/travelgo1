import os
import requests
from django.conf import settings

RESEND_API_KEY = getattr(settings, 'RESEND_API_KEY', os.getenv("RESEND_API_KEY", ""))

def send_resend_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Sends an email using Resend HTTPS REST API.
    Bypasses SMTP port blocks on PythonAnywhere Free.
    """
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    
    from_email = getattr(settings, 'RESEND_FROM_EMAIL', os.getenv("RESEND_FROM_EMAIL", "TravelGo <onboarding@resend.dev>"))
    
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Resend error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Resend exception: {e}")
        return False


def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Sends 4-digit verification OTP code to user's email via Resend.
    """
    subject = "TravelGo - თქვენი ვერიფიკაციის კოდი 🌍"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 2px solid #000; border-radius: 16px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #000; margin: 0; font-size: 26px; font-weight: 900;">TravelGo</h1>
            <p style="color: #666; font-size: 14px; margin-top: 4px;">Explore Georgia • Earn XP • AR Experience</p>
        </div>
        <div style="background-color: #f8f9fa; border: 1.5px solid #000; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;">
            <p style="font-size: 14px; color: #333; margin: 0 0 10px 0; font-weight: 600;">თქვენი ერთჯერადი 4-ნიშნა კოდია:</p>
            <div style="font-size: 36px; font-weight: 900; letter-spacing: 8px; color: #000; background-color: #E2FA31; padding: 12px 20px; border-radius: 10px; display: inline-block; border: 2px solid #000;">
                {otp_code}
            </div>
            <p style="font-size: 12px; color: #888; margin-top: 12px; margin-bottom: 0;">კოდი მოქმედებს 15 წუთის განმავლობაში.</p>
        </div>
        <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">თუ ეს მოთხოვნა თქვენ არ გაგიგზავნიათ, გთხოვთ უგულებელყოთ ეს წერილი.</p>
    </div>
    """
    return send_resend_email(email, subject, html)


def send_password_reset_email(email: str, pin: str) -> bool:
    """
    Sends password reset PIN via Resend.
    """
    subject = "TravelGo - პაროლის აღდგენა 🔑"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 2px solid #000; border-radius: 16px; background-color: #ffffff;">
        <h2 style="color: #000; font-weight: 900; margin-top: 0;">პაროლის აღდგენა</h2>
        <p style="color: #444; font-size: 14px;">თქვენი პაროლის აღდგენის კოდია:</p>
        <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #000; background-color: #E2FA31; padding: 10px 16px; border-radius: 8px; display: inline-block; border: 2px solid #000; margin: 10px 0;">
            {pin}
        </div>
        <p style="color: #777; font-size: 12px;">კოდი მოქმედებს 30 წუთის განმავლობაში.</p>
    </div>
    """
    return send_resend_email(email, subject, html)

