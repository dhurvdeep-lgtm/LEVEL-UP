#!/usr/bin/env python3
"""
Deepak Messenger Bot - Main Entry Point
Specialized for Deepak Kumar Kumar
"""

import os
import sys
from src.bot import MessengerBot
from src.message_manager import MessageManager
from src.friend_manager import FriendManager
from config.settings import Settings
from config.credentials import Credentials

def main():
    print("🚀 Deepak Messenger Bot")
    print("👤 Specialized for: Deepak Kumar Kumar")
    print("=" * 50)
    
    # Load settings and credentials
    settings = Settings()
    credentials = Credentials()
    
    # Initialize managers
    message_manager = MessageManager()
    friend_manager = FriendManager()
    
    # Check if Deepak is configured
    deepak_profile = friend_manager.get_friend("Deepak kumar kumar")
    if not deepak_profile:
        print("📝 Setting up Deepak for first time...")
        deepak_profile = setup_deepak_profile(friend_manager, message_manager)
    
    # Initialize bot
    bot = MessengerBot(settings=settings)
    
    try:
        # Login
        if bot.login(credentials.email, credentials.password):
            show_main_menu(bot, message_manager, friend_manager, deepak_profile)
        else:
            print("❌ Login failed!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.cleanup()

def setup_deepak_profile(friend_manager, message_manager):
    """Setup Deepak's profile for first time"""
    deepak_profile = {
        "name": "Deepak kumar kumar",
        "message_file": "Deepak_kumar_kumar.txt",
        "preferred_language": "hindi",
        "message_delay": 3,
        "relationship": "friend"
    }
    
    # Create profile
    friend_manager.create_friend(deepak_profile)
    
    # Create default messages
    default_messages = [
        "Hello Deepak! 👋",
        "Kaise ho aap?",
        "Python bot testing chal raha hai",
        "Ye message automatically bhej raha hoon",
        "Kuch kaam hai toh batana",
        "Bye! 😊"
    ]
    
    message_manager.create_message_file("Deepak kumar kumar", default_messages)
    print("✅ Deepak profile setup completed!")
    return deepak_profile

def show_main_menu(bot, message_manager, friend_manager, deepak_profile):
    """Show main menu"""
    while True:
        print(f"\n🎯 Main Menu - Deepak Kumar Kumar")
        print("-" * 40)
        print("1. Send messages to Deepak")
        print("2. Edit Deepak's messages")
        print("3. View message history")
        print("4. Send custom message")
        print("5. Check new messages")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            send_messages_to_deepak(bot, message_manager, deepak_profile)
        elif choice == "2":
            edit_deepak_messages(message_manager, deepak_profile)
        elif choice == "3":
            view_message_history(friend_manager, deepak_profile)
        elif choice == "4":
            send_custom_message(bot, deepak_profile)
        elif choice == "5":
            bot.check_new_messages()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option!")

def send_messages_to_deepak(bot, message_manager, deepak_profile):
    """Send messages to Deepak"""
    print(f"\n📨 Preparing to send messages to {deepak_profile['name']}...")
    
    messages = message_manager.get_messages("Deepak kumar kumar")
    if not messages:
        print("❌ No messages found for Deepak!")
        return
    
    print(f"📝 Found {len(messages)} messages")
    print("\nMessages to send:")
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. {msg}")
    
    confirm = input("\nSend these messages? (y/n): ").lower()
    if confirm == 'y':
        success = bot.send_messages("Deepak kumar kumar", messages)
        if success:
            print("✅ Messages sent successfully!")
        else:
            print("❌ Failed to send messages")

def edit_deepak_messages(message_manager, deepak_profile):
    """Edit messages for Deepak"""
    print(f"\n📝 Editing messages for {deepak_profile['name']}")
    message_manager.edit_messages_interactive("Deepak kumar kumar")

def view_message_history(friend_manager, deepak_profile):
    """View message history with Deepak"""
    history = friend_manager.get_message_history("Deepak kumar kumar")
    if history:
        print(f"\n📊 Message History with {deepak_profile['name']}:")
        for entry in history[-10:]:  # Last 10 messages
            print(f"  {entry['timestamp']}: {entry['message']}")
    else:
        print("📊 No message history found")

def send_custom_message(bot, deepak_profile):
    """Send custom message to Deepak"""
    message = input("Enter your custom message: ").strip()
    if message:
        success = bot.send_messages("Deepak kumar kumar", [message])
        if success:
            print("✅ Custom message sent!")
        else:
            print("❌ Failed to send message")

if __name__ == "__main__":
    main()
