from vigilant import collector, logger


def main():
    """Process for collecting expenses data and load it into a google
    spreadsheet
    """
    collector.collect()

    logger.info("Operation completed successfully")
