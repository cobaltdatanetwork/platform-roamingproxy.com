import logging
from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            result = session.exec(select(1)).first()
            logger.info("Database connection successful, result: %s", result)
    except Exception as e:
        logger.error("Failed to connect to database: %s", str(e))
        raise

def main() -> None:
    logger.info("Initializing service")
    try:
        init(engine)
        logger.info("Service finished initializing")
    except Exception as e:
        logger.error("Service initialization failed: %s", str(e))
        raise

if __name__ == "__main__":
    main()