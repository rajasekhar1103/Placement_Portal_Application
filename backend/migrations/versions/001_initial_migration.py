"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-05-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("role IN ('admin', 'company', 'student')", name='check_user_role'),
        sa.CheckConstraint('length(email) >= 5', name='check_email_length'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create companies table
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('hr_contact', sa.String(length=150), nullable=True),
        sa.Column('hr_phone', sa.String(length=20), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=True),
        sa.Column('is_blacklisted', sa.Boolean(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name='check_approval_status'),
        sa.CheckConstraint('length(company_name) > 0', name='check_company_name_not_empty'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create students table
    op.create_table('students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('roll_number', sa.String(length=50), nullable=True),
        sa.Column('branch', sa.String(length=100), nullable=True),
        sa.Column('cgpa', sa.Float(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('resume_path', sa.String(length=300), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('roll_number')
    )

    # Create placement_drives table
    op.create_table('placement_drives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('job_title', sa.String(length=200), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('eligibility_branch', sa.String(length=300), nullable=True),
        sa.Column('eligibility_cgpa', sa.Float(), nullable=True),
        sa.Column('eligibility_year', sa.Integer(), nullable=True),
        sa.Column('salary', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('interview_type', sa.String(length=50), nullable=True),
        sa.Column('application_deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('drive_id', sa.Integer(), nullable=False),
        sa.Column('application_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('interview_date', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['drive_id'], ['placement_drives.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive')
    )


def downgrade():
    op.drop_table('applications')
    op.drop_table('placement_drives')
    op.drop_table('students')
    op.drop_table('companies')
    op.drop_table('users')