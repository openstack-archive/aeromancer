"""add global_requirement table

Revision ID: 17770a76e3c7
Revises: 203851643975
Create Date: 2014-11-12 12:58:13.309422

"""

# revision identifiers, used by Alembic.
revision = '17770a76e3c7'
down_revision = '203851643975'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'global_requirement',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('line_id', sa.Integer,
                  sa.ForeignKey('line.id', name='fk_requirement_line_id')),
        sa.Column('name', sa.String()),
    )
    pass


def downgrade():
    op.drop_table('global_requirement')
    pass
