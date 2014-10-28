"""create project table

Revision ID: 575c6e7ef2ea
Revises: None
Create Date: 2014-10-27 22:32:51.240215

"""

# revision identifiers, used by Alembic.
revision = '575c6e7ef2ea'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('path', sa.String()),
    )


def downgrade():
    op.drop_table('project')
