"""Added age column

Revision ID: 3324dbd7cbea
Revises: da5f89276930
Create Date: 2025-04-25 14:10:45.289842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3324dbd7cbea'
down_revision: Union[str, None] = 'da5f89276930'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1) Добавляем пустое поле age
    op.add_column('user', sa.Column('age', sa.Integer(), nullable=True))

    # 2) Создаём функцию-триггер, которая на вставке/обновлении считает возраст
    op.execute("""
    CREATE FUNCTION update_user_age() RETURNS trigger AS $$
    BEGIN
        -- вычисляем возраст в годах и кладём в NEW.age
        NEW.age := DATE_PART('year', AGE(CURRENT_DATE, NEW.date_of_birth));
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 3) Привязываем функцию к таблице user
    op.execute("""
    CREATE TRIGGER trg_update_user_age
    BEFORE INSERT OR UPDATE ON "user"
    FOR EACH ROW
    EXECUTE FUNCTION update_user_age();
    """)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'age')
    # ### end Alembic commands ###
