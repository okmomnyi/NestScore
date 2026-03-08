import asyncio
import logging

from sqlalchemy import text

from app.database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_disagree_count():
    """Adds the disagree_count column to the reviews table."""
    logger.info("Starting database schema update...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if column exists first
            result = await db.execute(
                text(
                    "SELECT column_name "
                    "FROM information_schema.columns "
                    "WHERE table_name='reviews' AND column_name='disagree_count';"
                )
            )
            col = result.scalar_one_or_none()
            
            if col:
                logger.info("Column 'disagree_count' already exists on 'reviews' table. Skipping.")
                return

            logger.info("Adding 'disagree_count' column to 'reviews' table...")
            await db.execute(
                text("ALTER TABLE reviews ADD COLUMN disagree_count INT DEFAULT 0 NOT NULL;")
            )
            await db.commit()
            logger.info("Successfully added 'disagree_count' column.")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update database schema: {e}")


if __name__ == "__main__":
    asyncio.run(add_disagree_count())
