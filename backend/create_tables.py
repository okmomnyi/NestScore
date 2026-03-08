import asyncio
import sys
import os
from sqlalchemy import text

# Add the current directory to sys.path to allow imports from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
# Import all models to register them with Base.metadata
from app.models import plot, review, dispute, flag, plot_suggestion, audit_log

async def main():
    print("Creating tables on Neon Postgres...")
    async with engine.begin() as conn:
        # Check if column exists first or just run ALTER TABLE
        try:
            await conn.execute(text("ALTER TABLE reviews ADD COLUMN nickname VARCHAR(50)"))
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)
    print("Tables updated/created successfully.")

if __name__ == "__main__":
    asyncio.run(main())
