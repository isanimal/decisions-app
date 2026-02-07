"""v2.0-4 auth and teams

Revision ID: 0003_v2_0_4_auth
Revises: 0002_v2_0_3_threatlite_guided
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_v2_0_4_auth"
down_revision = "0002_v2_0_3_threatlite_guided"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("default_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
    )
    op.create_table(
        "memberships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="MEMBER"),
    )

    with op.batch_alter_table("decisions") as batch_op:
        batch_op.add_column(sa.Column("team_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("created_by", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_decisions_team_id", "teams", ["team_id"], ["id"])
        batch_op.create_foreign_key("fk_decisions_created_by", "users", ["created_by"], ["id"])
        batch_op.create_foreign_key("fk_decisions_updated_by", "users", ["updated_by"], ["id"])

    with op.batch_alter_table("decision_revisions") as batch_op:
        batch_op.add_column(sa.Column("created_by", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_revisions_created_by", "users", ["created_by"], ["id"])

    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.add_column(sa.Column("created_by", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_threat_created_by", "users", ["created_by"], ["id"])
        batch_op.create_foreign_key("fk_threat_updated_by", "users", ["updated_by"], ["id"])

def downgrade() -> None:
    with op.batch_alter_table("threat_lite_assessments") as batch_op:
        batch_op.drop_constraint("fk_threat_updated_by", type_="foreignkey")
        batch_op.drop_constraint("fk_threat_created_by", type_="foreignkey")
        batch_op.drop_column("updated_by")
        batch_op.drop_column("created_by")

    with op.batch_alter_table("decision_revisions") as batch_op:
        batch_op.drop_constraint("fk_revisions_created_by", type_="foreignkey")
        batch_op.drop_column("created_by")

    with op.batch_alter_table("decisions") as batch_op:
        batch_op.drop_constraint("fk_decisions_updated_by", type_="foreignkey")
        batch_op.drop_constraint("fk_decisions_created_by", type_="foreignkey")
        batch_op.drop_constraint("fk_decisions_team_id", type_="foreignkey")
        batch_op.drop_column("updated_by")
        batch_op.drop_column("created_by")
        batch_op.drop_column("team_id")

    op.drop_table("memberships")
    op.drop_table("users")
    op.drop_table("teams")
