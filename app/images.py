from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.user import User
    from .models.product import Product
    from .models.store import Store


def upload_image(obj: User | Product | Store, image):
    pass
