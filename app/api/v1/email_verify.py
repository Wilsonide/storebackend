from fastapi import (
    APIRouter,
    BackgroundTasks,
)

from app.core.config import settings
from app.core.deps import CurrentUser, DBSession
from app.services.verification_service import email_verification_service
from app.utils.mail import send_verification_email

router = APIRouter(tags=["Email Verification"], prefix="/auth")


@router.post("/verify-email/send")
async def send_verification_email_route(
    background_tasks: BackgroundTasks,
    session: DBSession,
    current_user: CurrentUser,
):
    """Generate a new verification token and send it via email."""
    raw_token = await email_verification_service.create(
        session,
        current_user_id=current_user.id,
    )

    # Send email asynchronously
    verification_link = f"{settings.frontend_url}/verify-email?token={raw_token}"

    background_tasks.add_task(
        send_verification_email,
        to_email=current_user.email,
        verification_link=verification_link,
    )

    return {"message": "Verification email sent"}


@router.get("/verify-email")
async def verify_email_route(
    token: str,
    session: DBSession,
):
    """Verify the email using the token."""
    # This will mark the token used and the user as verified
    result = await email_verification_service.verify(session, token)
    return result


@router.post("/verify-email/resend")
async def resend_verification_email_route(
    background_tasks: BackgroundTasks,
    session: DBSession,
    current_user: CurrentUser,
):
    """Re-send verification email. Generates a new token."""
    raw_token = await email_verification_service.create(
        session,
        current_user_id=current_user.id,
    )

    verification_link = f"{settings.frontend_url}/verify-email?token={raw_token}"

    background_tasks.add_task(
        send_verification_email,
        to_email=current_user.email,
        verification_link=verification_link,
    )

    return {"message": "Verification email resent"}
