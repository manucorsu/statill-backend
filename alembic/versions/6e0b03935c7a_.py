"""empty message

Revision ID: 6e0b03935c7a
Revises: 8c4083d52110
Create Date: 2025-09-21 02:06:15.425843

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e0b03935c7a"
down_revision: Union[str, None] = "8c4083d52110"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
