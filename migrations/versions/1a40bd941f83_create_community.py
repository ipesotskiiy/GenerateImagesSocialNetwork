"""create community

Revision ID: 1a40bd941f83
Revises: 27ce2466a07c
Create Date: 2025-03-04 15:51:59.458154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a40bd941f83'
down_revision: Union[str, None] = '27ce2466a07c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'community',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, index=True, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        # sa.Column('creator_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
