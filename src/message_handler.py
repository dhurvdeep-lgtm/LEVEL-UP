import os
import json
from datetime import datetime
from .utils import logger

class MessageHandler:
    def __init__(self, data_dir="data/messages"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs("data/logs", exist_ok=True)
    
    def read_messages(self, file_path):
        """Read messages from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                messages = [line.strip() for line in file if line.strip()]
            
            logger.info(f"Read {len(messages)} messages from {file_path}")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    def create_template(self, template_name, messages=None):
        """Create a message template file"""
        template_path = f"{self.data_dir}/templates/{template_name}.txt"
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        if not messages:
            messages = [
                "Hello! 👋",
                "This is a template message",
                "You can customize these messages",
                "Each line will be sent separately"
            ]
        
        try:
            with open(template_path, 'w', encoding='utf-8') as file:
                for msg in messages:
                    file.write(msg + '\n')
            
            logger.info(f"Template created: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return False
    
    def log_message_sent(self, friend_name, message, success=True):
        """Log message sending activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'friend': friend_name,
            'message': message[:100],  # Truncate long messages
            'success': success
        }
        
        log_file = "data/logs/message_log.json"
        try:
            with open(log_file, 'a') as file:
                file.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing log: {e}")
