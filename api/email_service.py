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


def _get_mail_config() -> ConnectionConfig:
    """
    Creates SMTP ConnectionConfig lazily at call time (not at module import time).
    This ensures Vercel serverless environment variables are available.
    """
    username = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
    password = os.getenv("SMTP_PASSWORD", "your_app_password")
    mail_from = os.getenv("MAIL_FROM", username)
    port = int(os.getenv("SMTP_PORT", 587))
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")

    logger.info(f"SMTP config: server={server}, port={port}, username={username}, mail_from={mail_from}")

    return ConnectionConfig(
        MAIL_USERNAME=username,
        MAIL_PASSWORD=password,
        MAIL_FROM=mail_from,
        MAIL_PORT=port,
        MAIL_SERVER=server,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )


async def send_ticket_email(email: str, full_name: str, registration_id: str):
    """
    Generates a QR code and sends an email ticket to the student.
    Raises exceptions on failure so the caller can handle them.
    """
    # Build config lazily
    conf = _get_mail_config()

    # Check if SMTP is configured
    if conf.MAIL_USERNAME == "your_email@gmail.com":
        logger.warning("SMTP not configured properly. Skipping actual email send.")
        return

    # Generate QR Code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(registration_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Save image to a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="ticket_qr_")
    with os.fdopen(fd, 'wb') as f:
        img.save(f, format="PNG")
    
    try:
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

    finally:
        # Always clean up temporary file
        try:
            os.remove(temp_path)
        except OSError:
            pass


async def send_rejection_email(email: str, full_name: str):
    """
    Sends a rejection/waitlist email to the student.
    """
    conf = _get_mail_config()

    if conf.MAIL_USERNAME == "your_email@gmail.com":
        logger.warning("SMTP not configured properly. Skipping actual email send.")
        return

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
        <h2 style="color: #FF5257; text-align: center;">Update on your Registration</h2>
        <p>Hi <strong>{full_name}</strong>,</p>
        <p>Thank you for your interest in the Parul University Event.</p>
        <p>Due to overwhelming response and limited capacity, we unfortunately cannot accommodate everyone. At this time, we are unable to offer you a ticket to the event.</p>
        <p>We appreciate your enthusiasm and hope to see you at our future events!</p>
        <br/>
        <p>Best regards,</p>
        <p>The Event Team</p>
    </div>
    """

    message = MessageSchema(
        subject="Update on your Event Registration",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Rejection email sent successfully to {email}")
