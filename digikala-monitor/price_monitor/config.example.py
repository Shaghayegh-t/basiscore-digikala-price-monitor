"""
Configuration file template
Copy this file to config.py and fill in your actual values
"""

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "YOUR_EMAIL@gmail.com",  # ایمیل خودتان
    "sender_password": "YOUR_APP_PASSWORD",   # رمز اپلیکیشن Gmail
    "recipient_email": "YOUR_EMAIL@gmail.com" # ایمیل دریافت‌کننده
}

# BasisCore Configuration
BASISCORE_CONFIG = {
    "server": "127.0.0.1:8080",
    "router": {
        "web": ["*"]
    }
}

# Scheduler Configuration
SCHEDULER_CONFIG = {
    "check_interval": 60  # بررسی هر 60 ثانیه
}

# Database Configuration
DATABASE_CONFIG = {
    "db_path": "prices.db"
}

# BasisCore Path
BASISCORE_PATH = r"C:\PATH\TO\BasisCore.Server.Edge"

# ==============================================
# راهنمای دریافت App Password برای Gmail:
# ==============================================
# 1. برو به: https://myaccount.google.com/security
# 2. فعال کن: 2-Step Verification
# 3. برو به: App passwords
# 4. یک رمز جدید برای Mail بساز
# 5. رمز 16 رقمی را در sender_password قرار بده