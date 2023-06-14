"""add columns in borrow table

Revision ID: 74bde6da23fe
Revises: 173c259a5f59
Create Date: 2023-06-14 22:57:07.900472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74bde6da23fe'
down_revision = '173c259a5f59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('borrow', schema=None) as batch_op:
        batch_op.add_column(sa.Column('book_title', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('member_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('approve_admin', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('return_admin', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('requested_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('approved_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('returned_date', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('borrow', schema=None) as batch_op:
        batch_op.drop_column('returned_date')
        batch_op.drop_column('approved_date')
        batch_op.drop_column('requested_date')
        batch_op.drop_column('return_admin')
        batch_op.drop_column('approve_admin')
        batch_op.drop_column('member_name')
        batch_op.drop_column('book_title')

    # ### end Alembic commands ###
