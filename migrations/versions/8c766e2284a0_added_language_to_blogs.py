"""added language to blogs

Revision ID: 8c766e2284a0
Revises: acf5c16a2050
Create Date: 2020-06-14 15:24:02.471623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c766e2284a0'
down_revision = 'acf5c16a2050'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blog', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('blog', 'language')
    # ### end Alembic commands ###
