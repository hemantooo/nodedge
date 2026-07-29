import os
import qrcode
import tempfile
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
import logging

load_dotenv()

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SMTP Configuration from Environment Variables
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USERNAME", "your_email@gmail.com"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", "your_app_password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "your_email@gmail.com"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 587)),
    MAIL_SERVER=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_ticket_email(email: str, full_name: str, registration_id: str):
    """
    Generates a QR code and sends an email ticket to the student asynchronously.
    """
    try:
        # Generate QR Code image in memory
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(registration_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="ticket_qr_")
        with os.fdopen(fd, 'wb') as f:
            img.save(f, format="PNG")
        
        # Determine if email configuration is somewhat valid before sending
        if conf.MAIL_USERNAME == "your_email@gmail.com":
            logger.warning("SMTP not configured properly. Skipping actual email send.")
            return

        # Prepare Email HTML body
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
            <h2 style="color: #985EFF; text-align: center;">You're In! 🎉</h2>
            <p>Hi <strong>{full_name}</strong>,</p>
            <p>Your registration for the Parul University Event is confirmed.</p>
            <p>Please find your unique QR code ticket attached to this email. You will need to show this QR code at the entrance.</p>
            <br/>
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px;">
                <p style="margin: 0;"><strong>Registration ID:</strong> <span style="font-family: monospace;">{registration_id}</span></p>
            </div>
            <br/>
            <p>We look forward to seeing you there!</p>
            <p style="font-size: 12px; color: #888;">If you did not request this registration, please ignore this email.</p>
        </div>
        """

        # Define the message schema
        message = MessageSchema(
            subject="Your Event Ticket & QR Code",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html,
            attachments=[temp_path]
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Ticket email sent successfully to {email}")
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except OSError:
            pass

    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")

