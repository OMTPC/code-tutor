"""Dropped UserModuleProgress table

Revision ID: a418bedbd014
Revises: e3f1f4415396
Create Date: 2025-01-30 16:19:37.065159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a418bedbd014'
down_revision = 'e3f1f4415396'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_module_progress')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_module_progress',
    sa.Column('UMPid', sa.INTEGER(), nullable=False),
    sa.Column('userid', sa.INTEGER(), nullable=False),
    sa.Column('moduleid', sa.INTEGER(), nullable=False),
    sa.Column('status', sa.VARCHAR(length=9), nullable=True),
    sa.Column('progress', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['moduleid'], ['module.moduleid'], ),
    sa.ForeignKeyConstraint(['userid'], ['user.userid'], ),
    sa.PrimaryKeyConstraint('UMPid')
    )
    # ### end Alembic commands ###
