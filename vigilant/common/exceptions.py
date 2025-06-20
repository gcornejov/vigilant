class VigilantException(Exception):
    """Base exception for any error in Vigilant app"""

    message: str = "Vigilant App Error"

    def __str__(self) -> str:
        return self.message


class DataCollectorException(VigilantException):
    """Base exception for any error in Data Collector process"""

    message: str = "Data Collection Error"


class DriverException(DataCollectorException):
    """Error while navigating through browser"""

    def __init__(self, screenshot_path: str):
        self.message = f"Error encountered while navigating through browser. Check last state screenshot in: {screenshot_path}"


class DownloadTimeout(DataCollectorException):
    """Timeout reached while waiting to download file"""

    def __init__(self, timeout: float):
        self.message = f"Download timeout reached. ({timeout} sec)"
