"""Added CareerQuestions, CareerStory, IndustryChallenge tables and add foreign key to CareerSuggestions

Revision ID: 50a0818235f6
Revises: 1b73361468ea
Create Date: 2025-02-28 17:18:07.716956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50a0818235f6'
down_revision = '1b73361468ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('career_question',
    sa.Column('CQid', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('yes_answer', sa.String(length=255), nullable=False),
    sa.Column('no_answer', sa.String(length=255), nullable=False),
    sa.Column('careersuggid', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['careersuggid'], ['career_suggestions.CSid'], ),
    sa.PrimaryKeyConstraint('CQid')
    )
    op.create_table('career_story',
    sa.Column('CSid', sa.Integer(), nullable=False),
    sa.Column('story', sa.Text(), nullable=False),
    sa.Column('careersuggid', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['careersuggid'], ['career_suggestions.CSid'], ),
    sa.PrimaryKeyConstraint('CSid')
    )
    op.create_table('industry_challenge',
    sa.Column('ICid', sa.Integer(), nullable=False),
    sa.Column('challenge_text', sa.Text(), nullable=False),
    sa.Column('careersuggid', sa.Integer(), nullable=False),
    sa.Column('example_solution', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['careersuggid'], ['career_suggestions.CSid'], ),
    sa.PrimaryKeyConstraint('ICid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('industry_challenge')
    op.drop_table('career_story')
    op.drop_table('career_question')
    # ### end Alembic commands ###
