"""
Add hospital columns migration script
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create hospitals table
    op.create_table(
        'hospitals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('admin_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True, default="active"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add hospital_id to departments table
    op.add_column('departments', sa.Column('hospital_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_departments_hospital_id', 'departments', 'hospitals', ['hospital_id'], ['id'])
    
    # Add hospital_id to doctors table
    op.add_column('doctors', sa.Column('hospital_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_doctors_hospital_id', 'doctors', 'hospitals', ['hospital_id'], ['id'])

def downgrade():
    # Remove foreign keys
    op.drop_constraint('fk_doctors_hospital_id', 'doctors', type_='foreignkey')
    op.drop_constraint('fk_departments_hospital_id', 'departments', type_='foreignkey')
    
    # Remove columns
    op.drop_column('doctors', 'hospital_id')
    op.drop_column('departments', 'hospital_id')
    
    # Drop hospitals table
    op.drop_table('hospitals')