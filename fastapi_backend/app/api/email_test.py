from fastapi import APIRouter
from fastapi import HTTPException

from app.core.config import settings

from app.services.email_service import (
    send_email,
)


router = APIRouter(
    prefix="/email-test",
    tags=["Email Test"],
)


# ============================================================
# TEST EMAIL
# ============================================================

@router.post("")
def test_email():

    try:

        send_email(

            to_email=settings.smtp_username,

            subject=(
                "Smart E-Commerce Email Test"
            ),

            body=(

                "Hello!\n\n"

                "This is a test email from "
                "the Smart E-Commerce "
                "application.\n\n"

                "SMTP email integration "
                "is working successfully.\n\n"

                "Regards,\n"
                "Smart E-Commerce Team"
            ),
        )

        return {

            "status": "success",

            "message":
                "Test email sent successfully",

        }

    except Exception as exc:

        print(
            "EMAIL TEST FAILED:",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Email sending failed: "
                f"{str(exc)}"
            ),
        ) from exc