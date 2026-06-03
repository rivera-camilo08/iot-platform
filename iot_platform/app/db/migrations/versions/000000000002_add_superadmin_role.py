"""add_superadmin_role

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-05-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "000000000002"
down_revision = "000000000001"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # PostgreSQL no permite ALTER TYPE dentro de una transacción por defecto
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'superadmin'")

def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de un ENUM fácilmente.
    # Para downgrade real habría que recrear el tipo.
    pass
