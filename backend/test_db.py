import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

async def test():
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[-1]}")
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            print("Connected successfully!")
            await conn.close()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
