"""
Initialize database tables and seed with data.
Run this script to set up your local PostgreSQL database.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database import Base
from app.models.plot import Plot
from app.models.review import Review
from app.models.dispute import Dispute
from app.models.plot_suggestion import PlotSuggestion
from app.models.audit_log import AuditLog


async def init_database():
    """Create all database tables."""
    print("Initializing database tables...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1]}")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("\nDropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            print("\nCreating new tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("\n" + "="*60)
        print("DATABASE TABLES CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nTables created:")
        print("  - plots")
        print("  - reviews")
        print("  - disputes")
        print("  - plot_suggestions")
        print("  - audit_log")
        print("\nNow running data seeding...")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError initializing database: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running (docker-compose up -d)")
        print("  2. Database credentials are correct in .env")
        print("  3. Database 'nestscore' exists")
        raise
    finally:
        await engine.dispose()


async def main():
    """Initialize database and seed data."""
    await init_database()
    
    print("\nImporting seed script...")
    from seed_data import seed_database
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
