import logging

class LoggingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_input(self, message: str):
        self.logger.info(f"⬆️  {message}")
        
    def log_output(self, message: str):
        self.logger.info(f"⬇️  {message}")
