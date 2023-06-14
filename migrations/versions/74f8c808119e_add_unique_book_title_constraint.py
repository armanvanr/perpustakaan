"""add 'unique' book title constraint

Revision ID: 74f8c808119e
Revises: ae9e091bfd76
Create Date: 2023-06-14 16:44:06.084070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74f8c808119e'
down_revision = 'ae9e091bfd76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['title'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###