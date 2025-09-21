"""empty message

Revision ID: ab85c4e4a6e8
Revises: 6e0b03935c7a
Create Date: 2025-09-21 02:08:49.304163

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ab85c4e4a6e8"
down_revision: Union[str, None] = "6e0b03935c7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
