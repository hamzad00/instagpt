import os
import json
import logging
import glob
from datetime import datetime
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_memory(user_id):
    path = f"user_memory_{user_id}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                memory = json.load(f)
            for msg in memory:
                if "timestamp" not in msg:
                    msg["timestamp"] = datetime.now().timestamp()
            return memory
        except Exception as e:
            logger.error(f"Error loading memory for user {user_id}: {str(e)}")
            return []
    return []

def save_memory(user_id, memory):
    path = f"user_memory_{user_id}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        logger.debug(f"Memory saved for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving memory for user {user_id}: {str(e)}")

def ask_gpt(messages):
    try:
        def get_last_user_message():
            for msg in reversed(messages):
                if msg.get("role") == "user" and msg.get("content"):
                    return msg["content"]
            return "No message"

        recent_messages = []
        message_count = 0
        for msg in reversed(messages):
            if message_count >= 10:
                break
            if "role" in msg and "content" in msg:
                recent_messages.insert(0, {
                    "role": msg["role"],
                    "content": msg["content"]
                })
                message_count += 1

        formatted_messages = [{
            "role": "system", 
            "content": "You are a helpful assistant responding to Instagram messages. Be concise, helpful, and friendly. You support responding in multiple languages including English and Persian/Farsi."
        }]
        formatted_messages.extend(recent_messages)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=formatted_messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as api_error:
            logger.error(f"Error calling OpenAI API: {str(api_error)}")
            last_message = get_last_user_message()
            return f"Thanks for your message about '{last_message}'. I'll get back to you shortly. (This is a fallback response due to OpenAI API limitations)"

    except Exception as e:
        logger.error(f"General error in ask_gpt function: {str(e)}")
        raise

def get_all_user_ids():
    try:
        files = glob.glob("user_memory_*.json")
        user_ids = [f.replace("user_memory_", "").replace(".json", "") for f in files]
        return user_ids
    except Exception as e:
        logger.error(f"Error getting user IDs: {str(e)}")
        return []

def get_user_info(user_id):
    try:
        memory = load_memory(user_id)
        message_count = len(memory)
        last_active = "Unknown"
        if message_count > 0 and "timestamp" in memory[-1]:
            last_active = datetime.fromtimestamp(memory[-1]["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "id": user_id,
            "message_count": message_count,
            "last_active": last_active
        }
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {str(e)}")
        return {
            "id": user_id,
            "message_count": 0,
            "last_active": "Unknown"
        }

# Placeholder for future: send message back to Instagram user
def send_instagram_message(user_id, message):
    logger.info(f"[SIMULATED] Sending to {user_id}: {message}")
    # اینجا می‌تونی بعداً کد ارسال دایرکت واقعی رو اضافه کنی