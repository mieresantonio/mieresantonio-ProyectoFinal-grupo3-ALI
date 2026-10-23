"""certificates table (fase 2: gamificacion y certificados)

Revision ID: a2b3c4d5e6f7
Revises: 7f2959eb8c08
Create Date: 2026-10-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = '7f2959eb8c08'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('learning_path_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=30), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_certificates_code'), 'certificates', ['code'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_certificates_code'), table_name='certificates')
    op.drop_table('certificates')
