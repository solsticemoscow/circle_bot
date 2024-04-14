"""NEW

Revision ID: 244fd49f52d0
Revises: 
Create Date: 2024-04-14 07:16:49.438121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '244fd49f52d0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Buttons',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('button_name', sa.String(length=100), nullable=True),
    sa.Column('button_text', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('hi_message', sa.Text(), nullable=True),
    sa.Column('channel', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=200), nullable=True),
    sa.Column('firstname', sa.String(length=200), nullable=True),
    sa.Column('lastname', sa.String(length=200), nullable=True),
    sa.Column('language_code', sa.String(length=20), nullable=True),
    sa.Column('profile_description', sa.Text(), nullable=True),
    sa.Column('time_added', sa.DateTime(), nullable=True),
    sa.Column('blocked', sa.Boolean(), nullable=True),
    sa.Column('is_whitelist', sa.Boolean(), nullable=True),
    sa.Column('is_premium', sa.Boolean(), nullable=True),
    sa.Column('is_subs', sa.Boolean(), nullable=True),
    sa.Column('task_status', sa.Boolean(), nullable=True),
    sa.Column('task', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Channels',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('channel_name', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Channels')
    op.drop_table('Users')
    op.drop_table('Data')
    op.drop_table('Buttons')
    # ### end Alembic commands ###
