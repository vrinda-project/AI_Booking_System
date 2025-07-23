"""Add agent role to user_role enum

Revision ID: add_agent_role
Revises: 
Create Date: 2023-07-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_agent_role'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL specific enum update
    op.execute("ALTER TYPE user_role ADD VALUE 'agent' AFTER 'doctor'")


def downgrade():
    # Cannot easily remove enum values in PostgreSQL
    # This is a no-op downgrade
    pass