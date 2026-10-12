"""Run database migration to add salary and industry fields."""

import asyncio
import asyncpg
from app.core.config import settings


async def run_migration():
    """Run the migration SQL."""
    
    # Convert async URL to regular postgres URL
    db_url = str(settings.DATABASE_URL).replace("postgresql+asyncpg", "postgresql")
    
    print(f"Connecting to database...")
    conn = await asyncpg.connect(db_url)
    
    try:
        print("Running migration...")
        
        # Add columns
        await conn.execute("""
            ALTER TABLE career_recommendations 
            ADD COLUMN IF NOT EXISTS salary_range_min INTEGER,
            ADD COLUMN IF NOT EXISTS salary_range_max INTEGER,
            ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(3) DEFAULT 'USD',
            ADD COLUMN IF NOT EXISTS salary_period VARCHAR(20) DEFAULT 'annual',
            ADD COLUMN IF NOT EXISTS industry_trend TEXT,
            ADD COLUMN IF NOT EXISTS market_growth TEXT;
        """)
        print("✅ Added new columns")
        
        # Add indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommendations_salary_min 
            ON career_recommendations(salary_range_min);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommendations_salary_max 
            ON career_recommendations(salary_range_max);
        """)
        print("✅ Created indexes")
        
        # Update existing records
        await conn.execute("""
            UPDATE career_recommendations 
            SET 
                salary_currency = 'USD',
                salary_period = 'annual'
            WHERE salary_currency IS NULL OR salary_period IS NULL;
        """)
        print("✅ Updated existing records")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
