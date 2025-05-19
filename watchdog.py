import os
import time
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure settings
WEBHOOK_URL = "http://localhost:5000/webhook"  # Local webhook endpoint
MEMORY_DIR = "."  # Directory to watch for user memory files
CHECK_INTERVAL = 5  # How often to check for changes (seconds)

class SimpleFileMonitor:
    """Simple file monitor to check for changes in user memory files"""
    
    def __init__(self):
        self.last_processed = {}  # Track when files were last processed
        
    def process_memory_file(self, user_id, file_path):
        """Process the memory file for new messages"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                memory = json.load(f)
                
            # Look for user messages that haven't been responded to
            needs_response = False
            if memory and memory[-1]["role"] == "user":
                needs_response = True
                message = memory[-1]["content"]
                
                logger.info(f"New message from user {user_id}: {message}")
                self.send_to_webhook(user_id, message)
                
            if not needs_response:
                logger.debug(f"No new messages to process for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error processing memory file: {str(e)}")
    
    def send_to_webhook(self, user_id, message):
        """Send a message to the webhook endpoint"""
        try:
            data = {
                "user_id": user_id,
                "message": message
            }
            
            logger.info(f"Sending to webhook: {data}")
            
            response = requests.post(WEBHOOK_URL, json=data)
            
            if response.status_code == 200:
                logger.info(f"Webhook response: {response.json()}")
            else:
                logger.error(f"Webhook error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending to webhook: {str(e)}")
    
    def check_for_changes(self):
        """Check all user memory files for changes"""
        try:
            # Get list of memory files
            files = [f for f in os.listdir(MEMORY_DIR) 
                    if f.startswith("user_memory_") and f.endswith(".json")]
            
            for file in files:
                file_path = os.path.join(MEMORY_DIR, file)
                user_id = file.replace("user_memory_", "").replace(".json", "")
                
                # Get the last modification time
                mod_time = os.path.getmtime(file_path)
                
                # Process if new or modified since last check
                if user_id not in self.last_processed or self.last_processed[user_id] < mod_time:
                    logger.info(f"Detected changes in memory file for user {user_id}")
                    self.last_processed[user_id] = mod_time
                    self.process_memory_file(user_id, file_path)
        
        except Exception as e:
            logger.error(f"Error checking for changes: {str(e)}")

def create_test_message():
    """Create a test user memory file with a message for testing"""
    try:
        test_user_id = "test_user_" + datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"user_memory_{test_user_id}.json"
        
        # Create a test message
        test_message = [
            {
                "role": "user",
                "content": "Hello, this is a test message from the watchdog script!",
                "timestamp": time.time()
            }
        ]
        
        # Save the test message
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(test_message, f, indent=2)
            
        logger.info(f"Created test message for user {test_user_id}")
        return test_user_id
        
    except Exception as e:
        logger.error(f"Error creating test message: {str(e)}")
        return None

if __name__ == "__main__":
    logger.info("Starting Instagram GPT Simple Monitor")
    
    # Ask if user wants to create a test message
    create_test = input("Do you want to create a test message? (y/n): ")
    if create_test.lower() == 'y':
        test_user_id = create_test_message()
        if test_user_id:
            logger.info(f"Test message created for user ID: {test_user_id}")
    
    # Initialize the monitor
    monitor = SimpleFileMonitor()
    
    try:
        logger.info(f"Monitoring directory: {MEMORY_DIR}")
        logger.info(f"Checking for changes every {CHECK_INTERVAL} seconds...")
        
        while True:
            monitor.check_for_changes()
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")