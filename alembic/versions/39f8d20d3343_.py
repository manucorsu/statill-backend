"""empty message

Revision ID: 39f8d20d3343
Revises: 7704bb71a5e4
Create Date: 2025-09-20 19:36:46.260919

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "39f8d20d3343"
down_revision: Union[str, None] = "7704bb71a5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
