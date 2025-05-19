# InstaGPT - Automated Instagram Response System

InstaGPT is a system that automatically responds to Instagram messages using OpenAI's GPT model. It maintains conversation history for each user and provides a simple admin interface to monitor conversations.

## Features

- 🤖 Automated responses to Instagram messages using GPT
- 💬 Conversation memory for each user
- 🧠 Contextual replies based on conversation history
- 🖥️ Simple admin interface to monitor conversations
- 🔒 Basic authentication for admin access
- 🌐 Support for multiple languages, including Persian/Farsi

## Setup and Installation

### Prerequisites

- Python 3.6+
- Flask
- OpenAI API Key

### Environment Variables

Set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SESSION_SECRET`: Secret key for Flask sessions (optional)
- `ADMIN_PASSWORD`: Password for admin access (default: admin123)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/instagpt.git
cd instagpt
