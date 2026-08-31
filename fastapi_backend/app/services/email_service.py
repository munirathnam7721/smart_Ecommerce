import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    """
    Send a plain-text email using Gmail SMTP.
    """

    if not to_email:
        raise ValueError(
            "Recipient email address is required"
        )

    # --------------------------------------------------------
    # CREATE EMAIL
    # --------------------------------------------------------

    message = MIMEMultipart()

    message["From"] = (
        f"{settings.smtp_from_name} "
        f"<{settings.smtp_from_email}>"
    )

    message["To"] = to_email

    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain",
            "utf-8",
        )
    )

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print("=" * 70)
    print("EMAIL DEBUG")
    print("SMTP HOST:", settings.smtp_host)
    print("SMTP PORT:", settings.smtp_port)
    print("SMTP USERNAME:", settings.smtp_username)
    print("FROM:", settings.smtp_from_email)
    print("TO:", to_email)
    print("SUBJECT:", subject)
    print("=" * 70)

    # --------------------------------------------------------
    # SMTP
    # --------------------------------------------------------

    try:

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=30,
        ) as server:

            # EHLO
            server.ehlo()

            # STARTTLS
            server.starttls()

            # EHLO again after TLS
            server.ehlo()

            # LOGIN
            server.login(
                settings.smtp_username,
                settings.smtp_password,
            )

            # SEND
            server.send_message(
                message
            )

        print("=" * 70)
        print("EMAIL SENT SUCCESSFULLY")
        print("TO:", to_email)
        print("=" * 70)

    except smtplib.SMTPAuthenticationError as exc:

        print("=" * 70)
        print("SMTP AUTHENTICATION FAILED")
        print(
            "Check Gmail username and App Password."
        )
        print("ERROR:", str(exc))
        print("=" * 70)

        raise

    except smtplib.SMTPException as exc:

        print("=" * 70)
        print("SMTP ERROR")
        print("ERROR:", str(exc))
        print("=" * 70)

        raise

    except Exception as exc:

        print("=" * 70)
        print("EMAIL SENDING FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc))
        print("=" * 70)

        raise