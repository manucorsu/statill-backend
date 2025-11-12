from __future__ import annotations
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from .models.user import User
    from .models.store import Store

import datetime

from .models.verification_code import VerificationCode

from .utils import utcnow

from .security import generate_verification_code

from .config import settings

import requests

from fastapi.exceptions import HTTPException


def send_email(destination_user: User, subject: str, htmlBody: str):
    response = requests.post(
        settings.mailgun_url,
        auth=("api", settings.mailgun_api_key),
        data={
            "from": f"Statill <{settings.mailgun_email_address}>",
            "to": f"{destination_user.first_names} {destination_user.last_name} <{destination_user.email}>",
            "subject": subject,
            "html": htmlBody,
        },
    )
    try:
        assert response.status_code == 200
    except AssertionError as ex:
        print(response)
        raise ex


verification_email_template = {
    "subject": {
        "email": "Activá tu cuenta de Statill",
        "password_reset": "Restablecé tu contraseña de Statill",
        "store_add": "{store_name} quiere agregarte como cajero en Statill",
    },
    "body": {
        "email": """
                 <html>
                    <h1>Activá tu cuenta de Statill</h1>
                    <p>Tu código es <b>{code}</b></p>
                 </html>
                 """,
        "password_reset": """
                          <html>
                            <h1>Restablecé tu contraseña de </h1>
                    <p>Tu código es <b>{code}</b></p>
                          </html>
                          """,
        "store_add": """
                    <html>
                        <h1>{store_name} quiere agregarte como cajero en Statill"/h1>
                    <p>Tu código es <b>{code}</b></p>
                    </html>
                     """,
    },
}


# Esto en realidad debería ir en auth pero se me hace circular con crud.user
def send_verification_code(
    session: Session,
    user: User,
    type: Literal["email", "password_reset", "store_add"] = "email",
    store: Store | None = None,
):
    match (type):
        case "email":
            if user.email_verified:
                raise HTTPException(400, "User email is already verified")
        case "password_reset":
            pass
        case "store_add":
            assert store is not None
    session.query(VerificationCode).filter(VerificationCode.user_id == user.id).delete()
    code = generate_verification_code()
    expires_at = utcnow() + datetime.timedelta(minutes=1440)

    verification = VerificationCode(
        user_id=user.id, code=code, expires_at=expires_at, type=type
    )
    session.add(verification)
    session.commit()
    store_name = str(store.name) if store else ""
    send_email(
        user,
        verification_email_template["subject"][type].format(store_name=store_name),
        htmlBody=verification_email_template["body"][type].format(
            code=code, store_name=store_name
        ),
    )
