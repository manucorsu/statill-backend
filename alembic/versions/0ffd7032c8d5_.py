"""empty message

Revision ID: 0ffd7032c8d5
Revises: e3ff50266e5a
Create Date: 2025-09-25 10:06:17.632343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ffd7032c8d5'
down_revision: Union[str, None] = 'e3ff50266e5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
