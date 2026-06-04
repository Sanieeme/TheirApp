import smtplib
from email.mime.text import MIMEText

SMTP_EMAIL = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

def send_mentor_email(mentor_email, mentee_name, mentee_email):

    subject = "New Mentee Assigned - Bono Foundation"

    body = f"""
    Hello Mentor,

    You have been assigned a new mentee.

    Name: {mentee_name}
    Email: {mentee_email}

    Please log into the system to view full details.

    Bono Foundation
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = mentor_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, mentor_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email failed:", e)