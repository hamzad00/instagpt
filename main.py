import json
import time
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session

# Register the datetime filter for Jinja templates
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime from a timestamp"""
    if not value:
        return ""
    if isinstance(value, str):
        value = float(value)
    return datetime.fromtimestamp(value).strftime(format)
from utils import load_memory, save_memory, ask_gpt, get_all_user_ids, get_user_info

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "instagpt_secret_key")

# Register Jinja filter for datetime formatting
app.jinja_env.filters['datetime'] = format_datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    password = request.form.get('password')

    if password == admin_password:
        session['logged_in'] = True
        flash('Login successful', 'success')
        return redirect(url_for('conversations'))
    else:
        flash('Invalid password', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/conversations')
def conversations():
    if not session.get('logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('index'))

    user_ids = get_all_user_ids()
    users = []

    for user_id in user_ids:
        memory = load_memory(user_id)
        last_message = memory[-1]['content'] if memory else "No messages"
        last_time = datetime.fromtimestamp(os.path.getmtime(f"user_memory_{user_id}.json")).strftime('%Y-%m-%d %H:%M:%S')

        users.append({
            'id': user_id,
            'last_message': last_message[:100] + '...' if len(last_message) > 100 else last_message,
            'last_time': last_time,
            'message_count': len(memory)
        })

    return render_template('conversations.html', users=users)

@app.route('/conversation/<user_id>')
def view_conversation(user_id):
    if not session.get('logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('index'))

    memory = load_memory(user_id)
    user_info = get_user_info(user_id)

    return render_template('conversations.html', 
                          conversation=memory, 
                          user_id=user_id,
                          user_info=user_info,
                          active_user=user_id)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            logger.error("No JSON data in request")
            return jsonify({"error": "No data provided"}), 400

        user_id = data.get('user_id')
        message = data.get('message')

        if not user_id or not message:
            logger.error(f"Missing required fields: {data}")
            return jsonify({"error": "Missing required fields (user_id or message)"}), 400

        logger.debug(f"Received message from user {user_id}: {message}")

        history = load_memory(user_id)
        history.append({"role": "user", "content": message, "timestamp": time.time()})

        try:
            reply = ask_gpt(history)
            logger.debug(f"Generated reply: {reply}")
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            reply = "I'm sorry, I couldn't process your message right now. Please try again later."

        history.append({"role": "assistant", "content": reply, "timestamp": time.time()})
        save_memory(user_id, history)

        # Note: Direct Instagram messaging would be implemented here in a production environment
        # This is where you would integrate with Instagram's API
        logger.debug(f"Would send to Instagram user {user_id}: {reply}")

        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear/<user_id>', methods=['POST'])
def clear_conversation(user_id):
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        save_memory(user_id, [])
        flash(f"Conversation history for user {user_id} cleared successfully", "success")
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        flash(f"Error clearing conversation: {str(e)}", "danger")

    return redirect(url_for('conversations'))

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        "status": "running",
        "version": "1.1.0-enhanced",
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)