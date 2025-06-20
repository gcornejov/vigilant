from vigilant import data_collector, logger, update_spreadsheet


def main():
    """Process for collecting expenses data and load it into a google
    spreadsheet
    """
    data_collector.main()
    update_spreadsheet.main()

    logger.info("Operation completed successfully")
