"""empty message

Revision ID: 7704bb71a5e4
Revises: 2c74875a1368, 4dbaf643b77b
Create Date: 2025-09-20 19:36:20.034447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7704bb71a5e4"
down_revision: Union[str, None] = ("2c74875a1368", "4dbaf643b77b")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
