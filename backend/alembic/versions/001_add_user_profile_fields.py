"""add user profile fields

Revision ID: 001
Revises: 
Create Date: 2025-09-04 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new fields to users table
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    
    # Remove old location field
    op.drop_column('users', 'location')


def downgrade() -> None:
    # Remove new fields
    op.drop_column('users', 'city')
    op.drop_column('users', 'age')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    
    # Re-add location field
    op.add_column('users', sa.Column('location', sa.String(), nullable=True))
