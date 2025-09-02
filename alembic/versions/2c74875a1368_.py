"""empty message

Revision ID: 2c74875a1368
Revises: 0d2804a0db2e, 3a006f20df78
Create Date: 2025-09-02 08:59:30.024650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2c74875a1368"
down_revision: Union[str, None] = ("0d2804a0db2e", "3a006f20df78")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
