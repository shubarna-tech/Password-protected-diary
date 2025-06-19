import random
import smtplib
from email.mime.text import MIMEText

otp_storage = {}

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'your_app_password'    # Use App Password if Gmail

def generate_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp
    return otp

def send_otp(email, otp):
    msg = MIMEText(f"Your OTP for Encrypted Diary login is: {otp}")
    msg['Subject'] = 'Your OTP for Encrypted Diary'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def validate_otp(email, user_otp):
    return otp_storage.get(email) == user_otp
