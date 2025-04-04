"""Added intro column to Module table

Revision ID: 2c59a0d33c26
Revises: 782cc13f5af2
Create Date: 2025-02-07 12:37:55.285123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c59a0d33c26'
down_revision = '782cc13f5af2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('module', schema=None) as batch_op:
        batch_op.add_column(sa.Column('intro', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('module', schema=None) as batch_op:
        batch_op.drop_column('intro')

    # ### end Alembic commands ###
