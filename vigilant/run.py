from vigilant import logger, update_spreadsheet
from vigilant.data_collector import DataCollector


def main():
    """Process for collecting expenses data and load it into a google
    spreadsheet
    """
    DataCollector().collect()
    update_spreadsheet.main()

    logger.info("Operation completed successfully")
