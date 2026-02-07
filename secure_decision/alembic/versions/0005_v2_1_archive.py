"""v2.1 archive flags

Revision ID: 0005_v2_1_archive
Revises: 0004_v2_0_5_comments_mentions
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_v2_1_archive"
down_revision = "0004_v2_0_5_comments_mentions"
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("decisions") as batch_op:
        batch_op.add_column(sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.add_column(sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.drop_column("archived")
    with op.batch_alter_table("decisions") as batch_op:
        batch_op.drop_column("archived")
