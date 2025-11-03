import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict


class EmailNotifier:
    """Sends email notifications for price drops"""
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 sender_email: str, sender_password: str, 
                 recipient_email: str):
        """
        Initialize email notifier
        
        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (usually 587 for TLS)
            sender_email: Sender email address
            sender_password: Sender email password (use App Password for Gmail)
            recipient_email: Recipient email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
    
    def send_price_drop_notification(self, product_info: Dict) -> bool:
        """
        Send email notification about price drop
        
        Args:
            product_info: Dict containing product details and price drop info
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🔔 کاهش قیمت: {product_info['name']}"
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Create HTML email body
            html_body = self._create_html_body(product_info)
            
            # Create plain text version
            text_body = self._create_text_body(product_info)
            
            # Attach both versions
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(html_body, "html", "utf-8")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Email sent for: {product_info['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _create_text_body(self, info: Dict) -> str:
        """Create plain text email body"""
        return f"""
کاهش قیمت محصول دیجیکالا!

محصول: {info['name']}

قیمت قبلی: {info['old_price']:,} تومان
قیمت جدید: {info['new_price']:,} تومان

کاهش قیمت: {info['price_drop']:,} تومان ({info['drop_percentage']:.1f}%)

لینک محصول:
{info['url']}

---
سیستم نظارت قیمت دیجیکالا
        """
    
    def _create_html_body(self, info: Dict) -> str:
        """Create HTML email body"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Tahoma, Arial, sans-serif;
            direction: rtl;
            text-align: right;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            max-width: 600px;
            margin: 0 auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #e6123d;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .product-name {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin: 20px 0;
        }}
        .price-info {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .price-row {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 16px;
        }}
        .old-price {{
            color: #999;
            text-decoration: line-through;
        }}
        .new-price {{
            color: #e6123d;
            font-size: 24px;
            font-weight: bold;
        }}
        .savings {{
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }}
        .button {{
            display: inline-block;
            background-color: #e6123d;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 کاهش قیمت!</h1>
        </div>
        
        <div class="product-name">
            {info['name']}
        </div>
        
        <div class="price-info">
            <div class="price-row">
                <span>قیمت قبلی:</span>
                <span class="old-price">{info['old_price']:,} تومان</span>
            </div>
            <div class="price-row">
                <span>قیمت جدید:</span>
                <span class="new-price">{info['new_price']:,} تومان</span>
            </div>
        </div>
        
        <div class="savings">
            💰 صرفه‌جویی: {info['price_drop']:,} تومان ({info['drop_percentage']:.1f}%)
        </div>
        
        <div style="text-align: center;">
            <a href="{info['url']}" class="button">
                🛒 مشاهده در دیجیکالا
            </a>
        </div>
        
        <div class="footer">
            سیستم نظارت قیمت دیجیکالا
        </div>
    </div>
</body>
</html>
        """


# Example usage
if __name__ == "__main__":
    # Test configuration (replace with your actual credentials)
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="YOUR_EMAIL@gmail.com",
        sender_password="YOUR_APP_PASSWORD",
        recipient_email="YOUR_EMAIL@gmail.com"
    )
    
    # Test notification
    test_product = {
        'name': 'گوشی موبایل سامسونگ مدل Galaxy S21',
        'url': 'https://www.digikala.com/product/dkp-123456/',
        'old_price': 15000000,
        'new_price': 13500000,
        'price_drop': 1500000,
        'drop_percentage': 10.0
    }
    
    notifier.send_price_drop_notification(test_product)