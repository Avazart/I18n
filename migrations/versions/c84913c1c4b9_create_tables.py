"""create tables

Revision ID: c84913c1c4b9
Revises: 11302f28443a
Create Date: 2023-08-13 09:33:38.846977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c84913c1c4b9'
down_revision: Union[str, None] = '11302f28443a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(' Langs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('short', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('flag', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('short')
    )
    op.create_table('Users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('lang_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lang_id'], [' Langs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Users')
    op.drop_table(' Langs')
    # ### end Alembic commands ###