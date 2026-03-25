"""
Configuration for Job Fetcher application.
Loads settings from environment variables (.env file) or uses hardcoded defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys and Credentials
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "ad780d51cfmsh315d145ff1dabc4p120394jsn0d7fbc8ac3a2")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "d5cccb0a")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "82fd07c6c040c9a4145ef1efa3e2d738")

# Email Configuration (optional - for notifications)
EMAIL = os.getenv("EMAIL", "gokul.jayakumar2005@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "Gokul@2005")
RECEIVER = os.getenv("RECEIVER", "gokulkrishc861@gmail.com")

# Telegram Configuration (optional - for notifications)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Scheduler Configuration
SCHEDULER_INTERVAL_HOURS = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "24"))

# LinkedIn RSS Feeds for India jobs
LINKEDIN_RSS_FEEDS = [
    "https://www.linkedin.com/jobs/search/?keywords=software%20engineer%20fresher&location=India&rss=true",
    "https://www.linkedin.com/jobs/search/?keywords=machine%20learning%20intern&location=India&rss=true",
    "https://www.linkedin.com/jobs/search/?keywords=frontend%20developer%20fresher&location=India&rss=true",
    "https://www.linkedin.com/jobs/search/?keywords=backend%20developer&location=India&rss=true",
    "https://www.linkedin.com/jobs/search/?keywords=full%20stack%20developer&location=India&rss=true"
]

# Job search queries for multiple APIs
QUERIES = [
    "software engineer fresher india",
    "machine learning intern india",
    "frontend developer fresher india",
    "backend developer junior india",
    "data scientist intern india"
]

