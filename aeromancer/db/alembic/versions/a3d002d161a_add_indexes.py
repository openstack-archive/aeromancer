"""add indexes

Revision ID: a3d002d161a
Revises: 22e0aa22ab8e
Create Date: 2014-11-24 14:24:29.824147

"""

# revision identifiers, used by Alembic.
revision = 'a3d002d161a'
down_revision = '22e0aa22ab8e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('file_project_idx', 'file', ['project_id'])
    op.create_index('line_file_idx', 'line', ['file_id'])


def downgrade():
    op.drop_index('line_file_idx', 'line')
    op.drop_index('file_project_idx', 'file')
