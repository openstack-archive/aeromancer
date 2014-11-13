"""track file hash

Revision ID: 22e0aa22ab8e
Revises: 1fb08a62dd91
Create Date: 2014-11-13 00:32:24.909035

"""

# revision identifiers, used by Alembic.
revision = '22e0aa22ab8e'
down_revision = '1fb08a62dd91'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('file', sa.Column('sha', sa.String))


def downgrade():
    op.drop_column('file', 'sha')
