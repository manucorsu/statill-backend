"""empty message

Revision ID: 252eac14abe7
Revises: 39f8d20d3343
Create Date: 2025-09-20 19:36:53.791169

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "252eac14abe7"
down_revision: Union[str, None] = "39f8d20d3343"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
