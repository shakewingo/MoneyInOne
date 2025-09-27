"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    op.create_index(op.f('ix_users_device_id'), 'users', ['device_id'], unique=False)

    # Create asset_types table
    op.create_table('asset_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_types_category'), 'asset_types', ['category'], unique=False)

    # Create assets table
    op.create_table('assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('purchase_currency', sa.String(length=3), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_type_id'], ['asset_types.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_asset_type_id'), 'assets', ['asset_type_id'], unique=False)
    op.create_index(op.f('ix_assets_purchase_date'), 'assets', ['purchase_date'], unique=False)
    op.create_index(op.f('ix_assets_symbol'), 'assets', ['symbol'], unique=False)
    op.create_index(op.f('ix_assets_user_id'), 'assets', ['user_id'], unique=False)

    # Create exchange_rates table
    op.create_table('exchange_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_currency', sa.String(length=3), nullable=False),
        sa.Column('to_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=15, scale=8), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_currency', 'to_currency', 'fetched_at', name='uq_exchange_rate_currencies_date')
    )
    op.create_index('idx_exchange_rates_currencies', 'exchange_rates', ['from_currency', 'to_currency'], unique=False)
    op.create_index('idx_exchange_rates_fetched_at', 'exchange_rates', ['fetched_at'], unique=False)

    # Create asset_prices table
    op.create_table('asset_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('change_24h', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('volume_24h', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('market_cap', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'asset_type', 'fetched_at', name='uq_asset_price_symbol_type_date')
    )
    op.create_index('idx_asset_prices_fetched_at', 'asset_prices', ['fetched_at'], unique=False)
    op.create_index('idx_asset_prices_symbol_type', 'asset_prices', ['symbol', 'asset_type'], unique=False)

    # Insert default asset types
    op.execute("""
        INSERT INTO asset_types (id, name, category, is_default, attributes) VALUES
        (gen_random_uuid(), 'Cash/Bank Account', 'cash', true, '{"required_fields": ["account_name"], "optional_fields": ["bank_name", "account_number"]}'),
        (gen_random_uuid(), 'Stock', 'stock', true, '{"required_fields": ["symbol"], "optional_fields": ["exchange", "sector", "shares"]}'),
        (gen_random_uuid(), 'Cryptocurrency', 'crypto', true, '{"required_fields": ["symbol"], "optional_fields": ["wallet_address", "network"]}'),
        (gen_random_uuid(), 'Bond', 'bond', true, '{"required_fields": ["issuer"], "optional_fields": ["maturity_date", "interest_rate", "face_value"]}'),
        (gen_random_uuid(), 'Real Estate', 'real_estate', true, '{"required_fields": ["property_type"], "optional_fields": ["location", "square_footage", "address"]}'),
        (gen_random_uuid(), 'Commodity', 'commodity', true, '{"required_fields": ["commodity_type"], "optional_fields": ["grade", "exchange"]}'),
        (gen_random_uuid(), 'Mutual Fund/ETF', 'fund', true, '{"required_fields": ["fund_name"], "optional_fields": ["expense_ratio", "fund_family"]}');
    """)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('asset_prices')
    op.drop_table('exchange_rates')
    op.drop_table('assets')
    op.drop_table('asset_types')
    op.drop_table('users')
