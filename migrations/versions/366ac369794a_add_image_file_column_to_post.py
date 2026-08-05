"""Add image_file column to Post

Revision ID: 366ac369794a
Revises: 
Create Date: 2026-01-06 19:05:04.240544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '366ac369794a'
down_revision = '0001_initial_tables'
branch_labels = None
depends_on = None


def upgrade():
    # image_file column is already created by the initial migration (0001_initial_tables).
    # This revision is kept as a no-op checkpoint to preserve the migration chain.
    pass


def downgrade():
    pass
