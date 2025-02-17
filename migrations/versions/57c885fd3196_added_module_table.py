"""Added Module table

Revision ID: 57c885fd3196
Revises: 
Create Date: 2025-01-30 15:12:51.349925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57c885fd3196'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('module',
    sa.Column('moduleid', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('locked', 'available', 'completed', name='module_status'), nullable=True),
    sa.PrimaryKeyConstraint('moduleid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('module')
    # ### end Alembic commands ###
