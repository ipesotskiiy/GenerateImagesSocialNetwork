"""create community roles

Revision ID: dbb47a3b1030
Revises: 0f297436eeb6
Create Date: 2025-03-09 15:26:59.037290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbb47a3b1030'
down_revision: Union[str, None] = '0f297436eeb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('community_membership',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('community_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('admin', 'moderator', 'user', name='communityroleenum'), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['community.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'community_id')
    )
    # op.drop_table('user_community')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_community',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('community_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['community.id'], name='user_community_community_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_community_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'community_id', name='user_community_pkey')
    )
    op.drop_table('community_membership')
    # ### end Alembic commands ###
