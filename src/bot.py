from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from .config import Config
from .utils import logger

class MessengerBot:
    def __init__(self, config=None):
        self.config = config or Config()
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, self.config.timeout)
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        options = webdriver.ChromeOptions()
        
        if self.config.headless:
            options.add_argument('--headless')
        
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return webdriver.Chrome(options=options)
    
    def login(self, email=None, password=None):
        """Login to Facebook"""
        email = email or self.config.email
        password = password or self.config.password
        
        try:
            logger.info("Logging in to Facebook...")
            self.driver.get("https://www.facebook.com")
            time.sleep(2)
            
            # Login process
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.driver.find_element(By.ID, "pass")
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.submit()
            
            time.sleep(5)
            
            # Check login success
            if "login" in self.driver.current_url.lower():
                logger.error("Login failed")
                return False
            
            logger.info("Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def send_messages_from_file(self, friend_name, file_path, delay=2):
        """Send messages from file line by line"""
        from .message_handler import MessageHandler
        
        msg_handler = MessageHandler()
        messages = msg_handler.read_messages(file_path)
        
        if not messages:
            return False
        
        if not self._select_friend(friend_name):
            return False
        
        logger.info(f"Sending {len(messages)} messages to {friend_name}")
        
        success_count = 0
        for i, message in enumerate(messages, 1):
            if self._send_single_message(message):
                success_count += 1
                logger.info(f"Sent {i}/{len(messages)}: {message[:50]}...")
                
                if i < len(messages):
                    time.sleep(delay)
            else:
                logger.error(f"Failed to send message {i}")
        
        logger.info(f"Successfully sent {success_count}/{len(messages)} messages")
        return success_count > 0
    
    def _select_friend(self, friend_name):
        """Select friend from messenger"""
        try:
            self.driver.get("https://www.messenger.com")
            time.sleep(3)
            
            # Search and select friend
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Search')]"))
            )
            search_btn.click()
            time.sleep(1)
            
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Messenger']"))
            )
            search_box.send_keys(friend_name)
            time.sleep(2)
            
            friend_result = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{friend_name}')]"))
            )
            friend_result.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Friend selection error: {e}")
            return False
    
    def _send_single_message(self, message):
        """Send a single message"""
        try:
            message_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']"))
            )
            message_box.send_keys(message)
            time.sleep(1)
            
            send_btn = self.driver.find_element(By.XPATH, "//div[@aria-label='Press Enter to send']")
            send_btn.click()
            
            return True
            
        except Exception as e:
            logger.error(f"Message sending error: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
