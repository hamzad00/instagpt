import json
import time
from utils import load_memory, save_memory, ask_gpt
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_id = data['user_id']
    message = data['message']

    history = load_memory(user_id)
    history.append({"role": "user", "content": message})
    reply = ask_gpt(history)
    history.append({"role": "assistant", "content": reply})
    save_memory(user_id, history)

    return {"reply": reply}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)