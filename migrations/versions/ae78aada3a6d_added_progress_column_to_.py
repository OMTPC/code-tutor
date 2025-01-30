"""Added progress column to UserModuleProgress table

Revision ID: ae78aada3a6d
Revises: f8826c208e71
Create Date: 2025-01-30 15:49:45.366831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae78aada3a6d'
down_revision = 'f8826c208e71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_module_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_module_progress', schema=None) as batch_op:
        batch_op.drop_column('progress')

    # ### end Alembic commands ###
