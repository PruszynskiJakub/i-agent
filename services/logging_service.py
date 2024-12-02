class LoggingService:
    @staticmethod
    def log_input(message: str):
        print(f"⬆️  {message}")
        
    @staticmethod
    def log_output(message: str):
        print(f"⬇️  {message}")
