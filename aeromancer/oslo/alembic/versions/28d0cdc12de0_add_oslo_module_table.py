"""add oslo module table

Revision ID: 28d0cdc12de0
Revises: None
Create Date: 2014-11-12 20:38:44.826444

"""

# revision identifiers, used by Alembic.
revision = '28d0cdc12de0'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'oslo_module',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('line_id', sa.Integer,
                  sa.ForeignKey('line.id', name='fk_oslo_module_line_id')),
        sa.Column('project_id', sa.Integer,
                  sa.ForeignKey('project.id', name='fk_oslo_module_project_id')),
        sa.Column('name', sa.String()),
    )


def downgrade():
    op.drop_table('oslo_module')
