"""ai scoring fields

Adds the two columns the scorer needs for question types that cannot be graded
by exact match: a reference answer on the question and the model's rationale
on the answer.

This revision reconstructs one that was applied to the Supabase database but
whose script was never committed - the database already reported
``b04e839b3a38`` as its version while no such script existed, which made
``alembic upgrade head`` fail with "Can't locate revision". The revision id is
therefore fixed, not generated. Both columns are nullable with no default, so
re-running against a database that already has them is the only hazard; see
the guards below.

Revision ID: b04e839b3a38
Revises: d4461ab5c237
Create Date: 2026-09-16 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b04e839b3a38'
down_revision: Union[str, Sequence[str], None] = 'd4461ab5c237'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    """Whether ``table.column`` already exists.

    Offline mode (``alembic upgrade --sql``) has no connection to inspect, so
    report the column as absent there and emit the unconditional DDL - which
    is what a generated script would contain anyway.
    """
    if context.is_offline_mode():
        return False
    return column in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    """Upgrade schema."""
    # Idempotent: the Supabase database was stamped at this revision with the
    # columns already in place, so a fresh `upgrade head` there must not fail
    # on a duplicate column.
    if not _has_column("quiz_questions", "ideal_answer"):
        op.add_column("quiz_questions", sa.Column("ideal_answer", sa.String(), nullable=True))
    if not _has_column("quiz_answers", "ai_feedback"):
        op.add_column("quiz_answers", sa.Column("ai_feedback", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    if _has_column("quiz_answers", "ai_feedback"):
        op.drop_column("quiz_answers", "ai_feedback")
    if _has_column("quiz_questions", "ideal_answer"):
        op.drop_column("quiz_questions", "ideal_answer")
