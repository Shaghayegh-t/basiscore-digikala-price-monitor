import asyncio
from price_monitor.notifier import EmailNotifier

# تنظیمات ایمیل شما
notifier = EmailNotifier(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email="YOUR_EMAIL@gmail.com",
    sender_password="YOUR_APP_PASSWORD",
    recipient_email="YOUR_EMAIL@gmail.com"
    
)

# یک محصول تست
test_product = {
    'name': 'ساعت مچی عقربه‌ای مردانه کوارتز اسکمی مدل 2205si',
    'url': 'https://www.digikala.com/product/dkp-18111827/',
    'old_price': 500000,
    'new_price': 450000,
    'price_drop': 50000,
    'drop_percentage': 10.0
}

print("📧 Sending test email...")
success = notifier.send_price_drop_notification(test_product)

if success:
    print("✅ Email sent! Check your inbox: ravenraisetnt@gmail.com")
else:
    print("❌ Email failed to send")