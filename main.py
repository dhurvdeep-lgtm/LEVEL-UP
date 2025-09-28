from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import atexit

APPSTATE_FILE = "appstate.json"
USER_FILE = "replied_users.json"


class MessengerAppStateBot:
    def __init__(self, headless=True, message_file="messages.txt", delay_between_messages=2):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 15)
        self.message_file = message_file
        self.delay_between_messages = delay_between_messages
        self.replied_users = self.load_replied_users()
        atexit.register(self.close)

    # ------------------ AppState ------------------
    def save_appstate(self):
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            data = {
                "cookies": self.driver.get_cookies(),
                "localStorage": self.driver.execute_script(
                    "var items = {}; for(var i=0;i<localStorage.length;i++){ var k = localStorage.key(i); items[k] = localStorage.getItem(k);} return items;"
                )
            }
            with open(APPSTATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
            print("💾 AppState saved")
        except Exception as e:
            print(f"❌ Error saving appstate: {e}")

    def load_appstate(self):
        try:
            if os.path.exists(APPSTATE_FILE):
                with open(APPSTATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.driver.get("https://www.facebook.com")
                time.sleep(2)
                for cookie in data.get("cookies", []):
                    if "sameSite" in cookie and cookie["sameSite"] == "None":
                        cookie["sameSite"] = "Strict"
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                for k, v in data.get("localStorage", {}).items():
                    self.driver.execute_script(f"localStorage.setItem('{k}', '{v}');")
                self.driver.refresh()
                time.sleep(5)
                print("✅ AppState loaded")
                return True
            return False
        except Exception as e:
            print(f"❌ Error loading appstate: {e}")
            return False

    # ------------------ User Tracking ------------------
    def load_replied_users(self):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def save_replied_users(self):
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.replied_users), f)

    def has_replied(self, user_id):
        return user_id in self.replied_users

    def mark_replied(self, user_id):
        self.replied_users.add(user_id)
        self.save_replied_users()

    # ------------------ Messages ------------------
    def read_messages_from_file(self):
        if not os.path.exists(self.message_file):
            print(f"❌ Message file '{self.message_file}' not found!")
            return []
        with open(self.message_file, "r", encoding="utf-8") as f:
            messages = [line.strip() for line in f if line.strip()]
        return messages

    # ------------------ Auto Reply ------------------
    def check_and_reply(self):
        messages = self.read_messages_from_file()
        if not messages:
            print("❌ No messages to send.")
            return

        self.driver.get("https://www.messenger.com")
        time.sleep(5)

        while True:
            try:
                unread_chats = self.driver.find_elements(By.XPATH, "//li//div[contains(@class,'unread')]")
                if unread_chats:
                    print(f"📩 Found {len(unread_chats)} unread messages")
                    for chat in unread_chats:
                        try:
                            chat.click()
                            time.sleep(3)

                            # user_id from URL
                            current_url = self.driver.current_url
                            if "t/" in current_url:
                                user_id = current_url.split("t/")[-1].split("?")[0]
                            else:
                                user_id = "unknown"

                            if self.has_replied(user_id):
                                print(f"⏩ Already replied to {user_id}")
                                continue

                            # Send messages line by line
                            msg_box = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
                            )
                            for i, message in enumerate(messages, 1):
                                msg_box.send_keys(message)
                                time.sleep(0.5)
                                msg_box.send_keys(Keys.ENTER)
                                print(f"✅ Sent message {i}/{len(messages)} to {user_id}")
                                if i < len(messages):
                                    time.sleep(self.delay_between_messages)

                            self.mark_replied(user_id)
                            time.sleep(2)
                        except Exception as e:
                            print(f"❌ Error replying: {e}")
                else:
                    print("⏳ No new messages")
                time.sleep(10)
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(10)

    def close(self):
        try:
            self.driver.quit()
            print("Browser closed.")
        except:
            pass


if __name__ == "__main__":
    print("⚠️ WARNING: Automating Facebook Messenger may violate Facebook’s Terms of Service.")

    bot = MessengerAppStateBot(headless=True, message_file="messages.txt", delay_between_messages=3)

    if not bot.load_appstate():
        print("⚠️ No AppState found. Login manually first.")
        bot.driver.get("https://www.facebook.com")
        input("Login manually, then press Enter to save AppState...")
        bot.save_appstate()

    bot.check_and_reply()
