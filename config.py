import os
from dotenv import load_dotenv

load_dotenv() 

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Google AI API Key
GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
# Notion API Key
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")

# Notion Database ID
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

# Validate required environment variables
required_vars = [
    "TELEGRAM_BOT_TOKEN",
    "OPENAI_API_KEY",
    "GOOGLE_AI_API_KEY",
    "NOTION_API_KEY",
    "NOTION_DATABASE_ID"
]

for var in required_vars:
    if not locals()[var]:
        raise EnvironmentError(f"{var} is not set in the environment variables.")
