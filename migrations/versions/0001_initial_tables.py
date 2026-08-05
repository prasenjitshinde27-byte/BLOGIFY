"""Initial tables - create user, post, like, comment

Revision ID: 0001_initial_tables
Revises: 
Create Date: 2026-08-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create 'user' table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('image_file', sa.String(length=20), nullable=False),
        sa.Column('password', sa.String(length=60), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )

    # Create 'post' table (includes image_file so migration 366ac369794a is a no-op)
    op.create_table(
        'post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('date_posted', sa.DateTime(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('image_file', sa.String(length=20), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create 'comment' table
    op.create_table(
        'comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('date_posted', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['post_id'], ['post.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    # NOTE: 'like' table is created by migration 689e53944df9_add_like_table


def downgrade():
    op.drop_table('comment')
    op.drop_table('post')
    op.drop_table('user')
