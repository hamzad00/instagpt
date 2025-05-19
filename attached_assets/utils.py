import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_memory(user_id):
    path = f"user_memory_{user_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_memory(user_id, memory):
    path = f"user_memory_{user_id}.json"
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

def ask_gpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']