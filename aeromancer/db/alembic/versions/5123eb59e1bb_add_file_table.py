"""add file table

Revision ID: 5123eb59e1bb
Revises: 575c6e7ef2ea
Create Date: 2014-10-30 12:54:15.087307

"""

# revision identifiers, used by Alembic.
revision = '5123eb59e1bb'
down_revision = '575c6e7ef2ea'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'file',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('project_id', sa.Integer,
                  sa.ForeignKey('project.id', name='fk_file_project_id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('path', sa.String()),
    )


def downgrade():
    op.drop_table('file')
