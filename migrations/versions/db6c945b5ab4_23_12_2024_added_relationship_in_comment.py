"""23.12.2024 Added relationship in Comment

Revision ID: db6c945b5ab4
Revises: b6caf9eba21c
Create Date: 2024-12-23 14:47:17.071468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db6c945b5ab4'
down_revision: Union[str, None] = 'b6caf9eba21c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###