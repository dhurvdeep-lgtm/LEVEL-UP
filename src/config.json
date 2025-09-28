import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.email = os.getenv('FB_EMAIL', '')
        self.password = os.getenv('FB_PASSWORD', '')
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.timeout = int(os.getenv('TIMEOUT', '10'))
        self.default_delay = int(os.getenv('DEFAULT_DELAY', '2'))
        
        # Validate required settings
        if not self.email or not self.password:
            raise ValueError("Facebook credentials not found in environment variables")
