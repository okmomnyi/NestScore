"""rename_plot_suggestion_columns

Revision ID: 001_rename_plot_suggestion
Revises: 
Create Date: 2026-03-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001_rename_plot_suggestion'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename 'name' -> 'suggested_name' and 'description' -> 'notes' in plot_suggestions
    # Use ALTER TABLE ... RENAME COLUMN (works in PostgreSQL 9.1+)
    with op.batch_alter_table('plot_suggestions') as batch_op:
        try:
            batch_op.alter_column('name', new_column_name='suggested_name')
        except Exception:
            pass  # Column may already be renamed

        try:
            batch_op.alter_column('description', new_column_name='notes')
        except Exception:
            pass  # Column may already be renamed or never existed


def downgrade() -> None:
    with op.batch_alter_table('plot_suggestions') as batch_op:
        try:
            batch_op.alter_column('suggested_name', new_column_name='name')
        except Exception:
            pass

        try:
            batch_op.alter_column('notes', new_column_name='description')
        except Exception:
            pass
