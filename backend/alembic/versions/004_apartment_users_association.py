"""Add apartment_users association table for many-to-many owner/tenant support.

Revision ID: 004
Revises: 003
Create Date: 2026-04-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create apartment_users association table
    op.create_table(
        'apartment_users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('apartment_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['apartment_id'], ['apartments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('apartment_id', 'user_id', 'role',
                            name='uq_apartment_user_role'),
    )

    # Create indexes for faster lookups
    op.create_index(
        'ix_apartment_users_apartment_id',
        'apartment_users',
        ['apartment_id']
    )
    op.create_index(
        'ix_apartment_users_user_id',
        'apartment_users',
        ['user_id']
    )


def downgrade() -> None:
    op.drop_index('ix_apartment_users_user_id', table_name='apartment_users')
    op.drop_index('ix_apartment_users_apartment_id', table_name='apartment_users')
    op.drop_table('apartment_users')
