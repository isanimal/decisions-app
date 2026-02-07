"""v2.0-1 lifecycle states

Revision ID: 0001_v2_0_1_lifecycle
Revises: 
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_v2_0_1_lifecycle"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("decisions") as batch_op:
        batch_op.add_column(sa.Column("superseded_by_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_decisions_superseded_by_id",
            "decisions",
            ["superseded_by_id"],
            ["id"],
        )

    op.execute("UPDATE decisions SET status = 'DRAFT' WHERE status = 'draft' OR status IS NULL")
    op.execute("UPDATE decisions SET status = 'ACTIVE' WHERE status = 'active'")

def downgrade() -> None:
    op.execute("UPDATE decisions SET status = 'draft' WHERE status = 'DRAFT'")
    op.execute("UPDATE decisions SET status = 'active' WHERE status = 'ACTIVE'")
    with op.batch_alter_table("decisions") as batch_op:
        batch_op.drop_constraint("fk_decisions_superseded_by_id", type_="foreignkey")
        batch_op.drop_column("superseded_by_id")
