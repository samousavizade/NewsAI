"""add phone number on user table

Revision ID: 7b036b3f5d2b
Revises: 
Create Date: 2024-07-14 08:45:01.962374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b036b3f5d2b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', column=sa.Column("phone_number", sa.String(), nullable=True))


def downgrade() -> None:
    pass
