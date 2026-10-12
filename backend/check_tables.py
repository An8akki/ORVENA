"""Quick script to verify database tables"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.db.session import engine

async def check_tables():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        tables = [row[0] for row in result]
        print(f"\n✅ Database connected successfully!")
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        return tables

if __name__ == "__main__":
    tables = asyncio.run(check_tables())
    if not tables:
        print("\n⚠️  No tables found - migrations may not have run")
    else:
        print(f"\n✨ Database is ready with {len(tables)} tables!")
