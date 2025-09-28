from flask import Flask, render_template, request, jsonify
import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RenderMessengerBot:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome for Render.com"""
        try:
            logger.info("Setting up Chrome driver for Render...")
            
            chrome_options = Options()
            
            # Render.com specific settings
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            
            # Performance optimizations
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            
            # Set user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Disable logging for performance
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            logger.info("Chrome driver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Driver setup failed: {e}")
            raise
    
    def quick_login(self, email, password):
        """Fast login method for Render"""
        try:
            logger.info("Attempting quick login...")
            
            # Use mobile version for faster loading
            self.driver.get("https://m.facebook.com")
            
            # Fast element finding
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "pass")
            login_button = self.driver.find_element(By.NAME, "login")
            
            # Quick input
            email_field.send_keys(email)
            password_field.send_keys(password)
            login_button.click()
            
            # Quick check for login success
            time.sleep(3)
            
            if "login" not in self.driver.current_url:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def send_quick_message(self, friend_name, message):
        """Send message quickly"""
        try:
            # Go directly to message URL (faster)
            self.driver.get(f"https://m.facebook.com/messages/t/{friend_name}")
            time.sleep(2)
            
            # Find message input
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "body"))
            )
            
            message_input.send_keys(message)
            
            # Find send button
            send_button = self.driver.find_element(By.XPATH, "//input[@value='Send']")
            send_button.click()
            
            logger.info(f"Message sent to {friend_name}")
            return True
            
        except Exception as e:
            logger.error(f"Message sending error: {e}")
            return False
    
    def close(self):
        """Close driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

# Global bot instance
bot_instance = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})

@app.route('/send-message', methods=['POST'])
def send_message():
    """API endpoint to send message"""
    global bot_instance
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        friend_name = data.get('friend_name', 'Deepak')
        message = data.get('message', 'Hello from Render Bot!')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"})
        
        # Initialize bot
        bot_instance = RenderMessengerBot()
        
        # Login
        if bot_instance.quick_login(email, password):
            # Send message
            if bot_instance.send_quick_message(friend_name, message):
                bot_instance.close()
                return jsonify({"success": True, "message": "Message sent successfully"})
            else:
                bot_instance.close()
                return jsonify({"success": False, "error": "Failed to send message"})
        else:
            bot_instance.close()
            return jsonify({"success": False, "error": "Login failed"})
            
    except Exception as e:
        if bot_instance:
            bot_instance.close()
        return jsonify({"success": False, "error": str(e)})

@app.route('/send-bulk', methods=['POST'])
def send_bulk_messages():
    """Send multiple messages"""
    global bot_instance
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        friend_name = data.get('friend_name', 'Deepak')
        messages = data.get('messages', ['Hello!', 'How are you?'])
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"})
        
        bot_instance = RenderMessengerBot()
        
        if bot_instance.quick_login(email, password):
            results = []
            for msg in messages:
                success = bot_instance.send_quick_message(friend_name, msg)
                results.append({"message": msg, "success": success})
                time.sleep(2)  # Small delay between messages
            
            bot_instance.close()
            return jsonify({"success": True, "results": results})
        else:
            bot_instance.close()
            return jsonify({"success": False, "error": "Login failed"})
            
    except Exception as e:
        if bot_instance:
            bot_instance.close()
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
