from pydantic import EmailStr
from app.integrations.celery.celery_app import celery_app
from app.transports.handlers.users.utils import (
    EmailService,
    create_token_for_confirm_email,
    generate_link_for_confirm_email,
)


@celery_app.task
def send_confirmation_email_task(
    user_email: EmailStr,
    url: str,
) -> None:
    token = create_token_for_confirm_email(data={'email': user_email})
    link = generate_link_for_confirm_email(url, token)

    email_service = EmailService()
    email_service.send_registration_confirm_link(user_email, link)


