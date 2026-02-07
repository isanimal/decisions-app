"""v2.0-5 comments and mentions

Revision ID: 0004_v2_0_5_comments_mentions
Revises: 0003_v2_0_4_auth
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_v2_0_5_comments_mentions"
down_revision = "0003_v2_0_4_auth"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("decision_id", sa.Integer(), sa.ForeignKey("decisions.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "mentions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id"), nullable=False),
        sa.Column("mentioned_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("mentions")
    op.drop_table("comments")
