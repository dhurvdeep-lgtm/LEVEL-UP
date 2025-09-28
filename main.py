#!/usr/bin/env python3
"""
Facebook Messenger Bot - Main Entry Point
Educational Purpose Only
"""

import os
import sys
from src.bot import MessengerBot
from src.message_handler import MessageHandler
from src.config import Config
from src.utils import logger, safe_input

def main():
    print("🚀 Facebook Messenger Bot")
    print("⚠️  Educational Purpose Only\n")
    
    # Load configuration
    config = Config()
    
    # Initialize bot
    bot = MessengerBot(config=config)
    
    try:
        # Login
        if bot.login():
            # Message handler
            msg_handler = MessageHandler()
            
            # Main menu
            while True:
                print("\n📋 Menu:")
                print("1. Send messages from file")
                print("2. Create message template")
                print("3. Check new messages")
                print("4. Logout and exit")
                
                choice = safe_input("Select option (1-4): ")
                
                if choice == "1":
                    send_messages_flow(bot, msg_handler)
                elif choice == "2":
                    create_template_flow(msg_handler)
                elif choice == "3":
                    bot.check_new_messages()
                elif choice == "4":
                    break
                else:
                    print("❌ Invalid option")
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        bot.close()

def send_messages_flow(bot, msg_handler):
    """Flow for sending messages from file"""
    friend_name = safe_input("Enter friend's name: ")
    file_path = safe_input("Enter messages file path (or press enter for default): ")
    
    if not file_path:
        file_path = "data/messages/default_messages.txt"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Send messages
    success = bot.send_messages_from_file(friend_name, file_path)
    if success:
        print("✅ Messages sent successfully!")
    else:
        print("❌ Failed to send messages")

def create_template_flow(msg_handler):
    """Flow for creating message templates"""
    template_name = safe_input("Enter template name: ")
    msg_handler.create_template(template_name)

if __name__ == "__main__":
    main()
