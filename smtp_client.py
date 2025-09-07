# smtp_client.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def smtp_client():
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "prashant979256@gmail.com"
    password = "gotl turr ljap qtzd"  # App password recommended
    receiver_email = "prashantasp4@gmail.com"

    try:
        # Create email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Test Email from Python (SMTP Assignment)"
        message.attach(MIMEText("Hello! This is a test email.", "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)

        # Send email
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        # Close connection
        server.quit()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    smtp_client()
