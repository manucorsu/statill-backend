"""empty message

Revision ID: 3db1b659d965
Revises: 0d2804a0db2e, 3a006f20df78
Create Date: 2025-09-05 11:29:44.073620

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3db1b659d965"
down_revision: Union[str, None] = ("0d2804a0db2e", "3a006f20df78")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
