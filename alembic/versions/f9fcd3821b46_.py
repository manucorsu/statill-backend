"""empty message

Revision ID: f9fcd3821b46
Revises: e3ff50266e5a
Create Date: 2025-09-25 10:34:11.752836

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9fcd3821b46"
down_revision: Union[str, None] = "e3ff50266e5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
