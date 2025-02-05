"""Added solution_type column to Solution table

Revision ID: 791ff547a99f
Revises: 9a902c746af6
Create Date: 2025-02-05 18:17:33.179217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '791ff547a99f'
down_revision = '9a902c746af6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solution', schema=None) as batch_op:
        batch_op.add_column(sa.Column('solution_type', sa.Enum('text', 'regex', name='solution_type'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solution', schema=None) as batch_op:
        batch_op.drop_column('solution_type')

    # ### end Alembic commands ###
