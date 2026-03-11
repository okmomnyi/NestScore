import asyncio
import os
import sys
from sqlalchemy import text

# Add the current directory to sys.path to allow imports from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
# Import all models to register them with Base.metadata
from app.models import plot, review, dispute, flag, plot_suggestion, audit_log

async def main():
    print("Starting database setup...")
    
    # 1. Create all tables first (if they don't exist)
    async with engine.begin() as conn:
        print("Creating tables if they don't exist...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables creation/verification complete.")

    # 2. Run migrations (ALTER cases)
    async with engine.begin() as conn:
        print("Running manual migrations...")
        
        # Add nickname to reviews if missing
        try:
            await conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS nickname VARCHAR(50)"))
            print("Verified 'nickname' column in 'reviews' table.")
        except Exception as e:
            print(f"Note: Could not add nickname: {e}")

        # Rename columns in plot_suggestions if they are old names
        try:
            await conn.execute(text("ALTER TABLE plot_suggestions RENAME COLUMN name TO suggested_name"))
            print("Renamed 'name' to 'suggested_name' in 'plot_suggestions'.")
        except Exception as e:
            # Column might already be named correctly
            if 'does not exist' in str(e).lower() or 'already exists' in str(e).lower():
                pass
            else:
                print(f"Note on renaming name: {e}")
                
        try:
            await conn.execute(text("ALTER TABLE plot_suggestions RENAME COLUMN description TO notes"))
            print("Renamed 'description' to 'notes' in 'plot_suggestions'.")
        except Exception as e:
            if 'does not exist' in str(e).lower():
                pass
            else:
                print(f"Note on renaming description: {e}")

    print("Database setup complete!")

if __name__ == "__main__":
    asyncio.run(main())
