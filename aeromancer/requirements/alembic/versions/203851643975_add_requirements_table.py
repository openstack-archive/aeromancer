"""add requirements table

Revision ID: 203851643975
Revises: None
Create Date: 2014-11-04 14:02:12.847385

"""

# revision identifiers, used by Alembic.
revision = '203851643975'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'requirement',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('line_id', sa.Integer,
                  sa.ForeignKey('line.id', name='fk_requirement_line_id')),
        sa.Column('project_id', sa.Integer,
                  sa.ForeignKey('project.id', name='fk_requirement_project_id')),
        sa.Column('name', sa.String()),
    )


def downgrade():
    op.drop_table('requirement')
