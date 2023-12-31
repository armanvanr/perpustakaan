"""create tables and models

Revision ID: 684417b6543b
Revises: 
Create Date: 2023-06-17 19:31:33.791084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '684417b6543b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('birth_year', sa.SmallInteger(), nullable=True),
    sa.Column('is_show', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('author', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_author_id'), ['id'], unique=True)

    op.create_table('book',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('pages', sa.SmallInteger(), nullable=False),
    sa.Column('publisher', sa.String(), nullable=True),
    sa.Column('published_year', sa.SmallInteger(), nullable=True),
    sa.Column('is_show', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_book_id'), ['id'], unique=True)

    op.create_table('genre',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_show', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('genre', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_genre_id'), ['id'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('is_show', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_id'), ['id'], unique=True)

    op.create_table('book_author_table',
    sa.Column('book_id', sa.String(), nullable=False),
    sa.Column('author_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'author_id')
    )
    op.create_table('book_genre_table',
    sa.Column('book_id', sa.String(), nullable=False),
    sa.Column('genre_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )
    op.create_table('borrow',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('book_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('book_title', sa.String(), nullable=True),
    sa.Column('member_name', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('approve_admin', sa.String(), nullable=True),
    sa.Column('return_admin', sa.String(), nullable=True),
    sa.Column('requested_date', sa.Date(), nullable=True),
    sa.Column('approved_date', sa.Date(), nullable=True),
    sa.Column('returned_date', sa.Date(), nullable=True),
    sa.Column('is_show', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('borrow', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_borrow_id'), ['id'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('borrow', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_borrow_id'))

    op.drop_table('borrow')
    op.drop_table('book_genre_table')
    op.drop_table('book_author_table')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_id'))

    op.drop_table('user')
    with op.batch_alter_table('genre', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_genre_id'))

    op.drop_table('genre')
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_book_id'))

    op.drop_table('book')
    with op.batch_alter_table('author', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_author_id'))

    op.drop_table('author')
    # ### end Alembic commands ###
