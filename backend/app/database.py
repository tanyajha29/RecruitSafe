import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.user import User
from app.models.analysis import Analysis
from app.models.notification import Notification
from app.models.password_reset import PasswordResetToken
from app.models.cache import CacheEntry

logger = logging.getLogger("recruitsafe")

# List of all Beanie ODM models to register
document_models = [
    User,
    Analysis,
    Notification,
    PasswordResetToken,
    CacheEntry
]

async def init_db() -> None:
    """
    Initializes the connection to MongoDB Atlas or local MongoDB using the Motor async driver
    and registers all Beanie Document models.
    """
    try:
        logger.info("Initializing database connection...")
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        
        # Mock append_metadata to resolve Beanie/Motor compatibility issues on PyMongo 4.13+
        client.append_metadata = lambda *args, **kwargs: None
        
        # Parse database name from the connection URI, fallback to 'recruitsafe'
        db_name = "recruitsafe"
        try:
            # e.g., mongodb+srv://user:pass@host/dbname?options
            path_parts = settings.MONGODB_URI.split("/")
            if len(path_parts) > 3:
                db_part = path_parts[3].split("?")[0]
                if db_part:
                    db_name = db_part
        except Exception as e:
            logger.warning(f"Failed to parse db_name from MONGODB_URI, using default: {e}")

        logger.info(f"Target Database Name: {db_name}")
        await init_beanie(
            database=client[db_name],
            document_models=document_models
        )
        logger.info("Database and Beanie ODM successfully initialized.")
    except Exception as e:
        logger.error(f"Critical: Failed to initialize MongoDB connection: {e}")
        raise e
