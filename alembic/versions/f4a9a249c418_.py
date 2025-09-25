"""empty message

Revision ID: f4a9a249c418
Revises: 9ae352afb078, e2afe13c706f
Create Date: 2025-09-25 10:39:42.800846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4a9a249c418'
down_revision: Union[str, None] = ('9ae352afb078', 'e2afe13c706f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
