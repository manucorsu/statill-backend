from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.user import User

from .config import settings

import requests


def send_email(destination_user: User, subject: str, htmlBody: str):
    response = requests.post(
        settings.mailgun_url,
        auth=("api", settings.mailgun_api_key),
        data={
            "from": f"Statill <{settings.mailgun_email_address}>",
            "to": f"{destination_user.first_names} {destination_user.last_name} <{destination_user.email}>",
            "subject": subject,
            "html":htmlBody
        },
    )
    try:
        assert response.status_code == 200
    except AssertionError as ex:
        print(response)
        raise ex
