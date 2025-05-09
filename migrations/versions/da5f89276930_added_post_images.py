"""Added post images

Revision ID: da5f89276930
Revises: fa8921c5a3ef
Create Date: 2025-04-24 16:56:12.313775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da5f89276930'
down_revision: Union[str, None] = 'fa8921c5a3ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('thumbnail_url', sa.String(), nullable=True),
    sa.Column('uploaded_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_images_id'), 'post_images', ['id'], unique=False)
    op.create_index(op.f('ix_post_images_post_id'), 'post_images', ['post_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_images_post_id'), table_name='post_images')
    op.drop_index(op.f('ix_post_images_id'), table_name='post_images')
    op.drop_table('post_images')
    # ### end Alembic commands ###
