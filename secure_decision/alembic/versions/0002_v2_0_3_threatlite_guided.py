"""v2.0-3 threatlite guided prompts

Revision ID: 0002_v2_0_3_threatlite_guided
Revises: 0001_v2_0_1_lifecycle
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_v2_0_3_threatlite_guided"
down_revision = "0001_v2_0_1_lifecycle"
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.add_column(sa.Column("reflection_rationale", sa.Text(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("guided_mode", sa.Boolean(), nullable=False, server_default=sa.true()))

def downgrade() -> None:
    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.drop_column("guided_mode")
        batch_op.drop_column("reflection_rationale")
