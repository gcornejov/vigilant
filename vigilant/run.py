import asyncio

from vigilant import logger
from vigilant.core import collector, update_spreadsheet


def main():
    """Process for collecting expenses data and load it into a google
    spreadsheet
    """
    asyncio.run(collector.collect())
    update_spreadsheet.main()

    logger.info("Operation completed successfully")
