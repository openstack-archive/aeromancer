"""add line table

Revision ID: 1fb08a62dd91
Revises: 5123eb59e1bb
Create Date: 2014-10-30 17:52:17.984359

"""

# revision identifiers, used by Alembic.
revision = '1fb08a62dd91'
down_revision = '5123eb59e1bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'line',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('file_id', sa.Integer,
                  sa.ForeignKey('file.id', name='fk_line_file_id')),
        sa.Column('number', sa.Integer, nullable=False),
        sa.Column('content', sa.String()),
    )


def downgrade():
    op.drop_table('line')
