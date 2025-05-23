"""added delete community with author

Revision ID: 618deab4ac6e
Revises: 67ad0dc9cb8f
Create Date: 2025-04-06 15:57:11.004651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '618deab4ac6e'
down_revision: Union[str, None] = '67ad0dc9cb8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('community_creator_id_fkey', 'community', type_='foreignkey')
    op.create_foreign_key(None, 'community', 'user', ['creator_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'community', type_='foreignkey')
    op.create_foreign_key('community_creator_id_fkey', 'community', 'user', ['creator_id'], ['id'])
    # ### end Alembic commands ###
