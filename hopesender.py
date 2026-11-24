# pip install python-dotenv

import smtplib
import time
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

# --- HOPESENDER CONFIG ---
# Use your own domain + SMTP. Don't use free Gmail for bulk, it will block you.
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")  # or smtp.sendgrid.net, smtp.zoho.com, mail.yourdomain.com
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "you@yourdomain.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your_app_password")

SENDER_NAME = "Hopesender"
SENDER_EMAIL = SMTP_USER  # Must match your authenticated domain

# HTML Template
def build_email(to_name, subject, message_body):
    html = f"""
    <html>
    <body style="font-family: Arial; color:#222; line-height:1.6;">
        <p>Hi {to_name},</p>
        <p>{message_body}</p>
        <p>Best regards,<br><b>Hopesender</b><br>Your Growth Partner</p>
        <hr>
        <p style="font-size:12px; color:#888;">
        You received this because you are a business contact. 
        If you don't want future emails, <a href="https://yourdomain.com/unsubscribe?email=UNSUBSCRIBE_LINK">unsubscribe here</a>.
        </p>
    </body>
    </html>
    """
    return html

def send_one_email(to_email, to_name, subject, message_body):
    msg = MIMEMultipart('alternative')
    # This is the name that shows in inbox: "Hopesender"
    msg['From'] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Reply-To'] = SENDER_EMAIL
    # Proper headers = better inbox placement
    msg['X-Mailer'] = 'Hopesender v1.0'
    msg['List-Unsubscribe'] = f'<mailto:{SENDER_EMAIL}?subject=unsubscribe>'

    text_version = f"Hi {to_name},\n\n{message_body}\n\nBest regards,\nHopesender"
    html_version = build_email(to_name, subject, message_body)

    msg.attach(MIMEText(text_version, 'plain'))
    msg.attach(MIMEText(html_version, 'html'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"✅ Sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed {to_email}: {e}")
        return False

def send_bulk_from_csv(csv_file, subject, message_body, delay_seconds=15):
    """Send to a CSV from your Email Finder. CSV must have: name, emails"""
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', 'there')
            emails_str = row.get('emails', '')
            # Take first email only
            to_email = emails_str.split(',')[0].strip()
            if '@' not in to_email or 'Not found' in to_email:
                continue
            send_one_email(to_email, name, subject, message_body)
            print(f"Waiting {delay_seconds}s to protect reputation...")
            time.sleep(delay_seconds)

if __name__ == "__main__":
    # --- TEST: Send 1 email ---
    send_one_email(
        to_email="test@example.com",
        to_name="John",
        subject="Quick question about your business",
        message_body="I found your business and I wanted to ask if you need help getting more customers this month?"
    )

    # --- BULK: Uncomment to send to CSV from Email Finder ---
    # send_bulk_from_csv(
    #     csv_file="business_emails.csv",
    #     subject="Quick question about your business",
    #     message_body="I found your business and I wanted to ask if you need help getting more customers this month?",
    #     delay_seconds=20
    # )