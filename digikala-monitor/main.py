import sys
import os

# Load config
try:
    from config import (
        EMAIL_CONFIG, 
        BASISCORE_CONFIG, 
        SCHEDULER_CONFIG, 
        DATABASE_CONFIG,
        BASISCORE_PATH
    )
except ImportError:
    print("❌ Error: config.py not found!")
    print("📝 Please copy config.example.py to config.py and fill in your details")
    sys.exit(1)

# Add BasisCore to path
sys.path.insert(0, BASISCORE_PATH)

import json
import asyncio
import threading
import time
from bclib import edge
from price_monitor.scheduler import PriceScheduler
from price_monitor.database import PriceDatabase
from price_monitor.notifier import EmailNotifier
from price_monitor.scraper import DigikalaScraper

# BasisCore Edge configuration
app = edge.from_options(BASISCORE_CONFIG)

# Initialize components
db = PriceDatabase(**DATABASE_CONFIG)
scraper = DigikalaScraper()
notifier = EmailNotifier(**EMAIL_CONFIG)
scheduler = PriceScheduler(db, scraper, notifier, **SCHEDULER_CONFIG)

@app.web_action(app.url(""))
def home(context: edge.WebContext):
    """صفحه اصلی: نمایش تمام محصولات تحت نظارت"""
    products = db.get_all_products()

    html = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>نظارت قیمت دیجیکالا</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #f8f9fb; }
            .card { transition: transform 0.2s, box-shadow 0.2s; }
            .card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
            .fade-in { animation: fadeIn 0.5s ease-in-out; }
            @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
        </style>
    </head>
    <body class="font-sans bg-gray-50">
        <div class="max-w-5xl mx-auto py-10 px-4">
            <h1 class="text-3xl font-bold text-[#e6123d] mb-8 flex items-center gap-2">
                🛒 نظارت قیمت محصولات دیجیکالا
            </h1>
            
            <div class="bg-white shadow-sm rounded-2xl p-6 mb-10 border border-gray-200">
                <h2 class="text-xl font-semibold mb-4 text-gray-700">افزودن محصول جدید</h2>
                <form action="/add" method="post" class="flex flex-col sm:flex-row gap-3">
                    <input type="text" name="url" placeholder="لینک محصول دیجیکالا"
                        class="flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#e6123d] focus:border-[#e6123d]" required>
                    <button type="submit"
                        class="bg-[#e6123d] text-white px-6 py-3 rounded-xl hover:bg-[#c50f33] transition">
                        افزودن
                    </button>
                </form>
                <p class="text-sm text-gray-500 mt-3">🔁 بررسی خودکار هر دقیقه انجام می‌شود.</p>
            </div>
            
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">محصولات در حال نظارت</h2>
    """

    if products:
        html += '<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">'
        for prod in products:
            label_html = ""
            price_change_html = ""

            # بررسی تغییر قیمت
            if prod.get("price_dropped"):
                label_html = """
                <span class="inline-block bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded-full mb-2">
                    📉 کاهش قیمت!
                </span>
                """
                price_change_html = f"""
                    <p class="text-sm text-gray-500 line-through mb-1">
                        قیمت قبل: {prod['old_price']:,}ریال
                    </p>
                """
            elif prod.get("price_increased"):
                label_html = """
                <span class="inline-block bg-red-100 text-red-800 text-xs font-semibold px-2 py-1 rounded-full mb-2">
                    📈 افزایش قیمت!
                </span>
                """
                price_change_html = f"""
                    <p class="text-sm text-gray-500 line-through mb-1">
                        قیمت قبل: {prod['old_price']:,} ریال
                    </p>
                """

            html += f"""
            <div class="card bg-white rounded-2xl shadow-sm border border-gray-200 p-5 fade-in">
                {label_html}
                <h3 class="text-lg font-semibold text-gray-800 mb-2">{prod['name']}</h3>
                <p class="text-sm text-gray-600 mb-1">قیمت فعلی:</p>
                <p class="text-xl font-bold text-[#e6123d] mb-2">{prod['current_price']:,}ریال</p>
                {price_change_html}
                <p class="text-sm text-gray-600 mb-1">
                    کمترین قیمت: <span class="font-semibold">{prod['lowest_price']:,}ریال</span>
                </p>
                <p class="text-xs text-gray-500 mb-3">آخرین بررسی: {prod['last_checked']}</p>
                <a href="{prod['url']}" target="_blank"
                class="inline-block text-center w-full bg-[#e6123d] text-white py-2 rounded-xl hover:bg-[#c50f33] transition">
                مشاهده در دیجیکالا
                </a>
            </div>
            """
        html += "</div>"

    else:
        html += """
        <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-5 text-center text-yellow-800">
            هنوز هیچ محصولی اضافه نشده است 🙁<br>
            لطفاً لینک یک محصول دیجیکالا را وارد کنید تا نظارت آغاز شود.
        </div>
        """

    html += """
        </div>
    </body>
    </html>
    """
    return html



@app.web_action(app.url("add"))
async def add_product(context: edge.WebContext):
    """Add a new product to monitor"""
    
    url = context.cms.get('form', {}).get('url')
    
    if url and 'digikala.com/product/' in url:
        print(f"🔍 Scraping product: {url}")
        
        # ✅ Await the async scraper
        product_info = await scraper.scrape_product(url)
        
        if product_info:
            success = db.add_product(
                url=url,
                name=product_info['name'],
                price=product_info['price']
            )
            
            if success:
                return f"<h1>محصول اضافه شد: {product_info['name']}</h1>"
            else:
                return "<h1>این محصول قبلاً اضافه شده است</h1>"
        else:
            return "<h1>خطا در دریافت اطلاعات محصول</h1>"
    
    return "<h1>لینک نامعتبر</h1>"


@app.web_action(app.url("status"))
def status(context: edge.WebContext):
    """API endpoint to get status as JSON"""
    products = db.get_all_products()
    # context.response.type = edge.ResponseTypes.JSON
    return json.dumps({
        "total_products": len(products),
        "products": products,
        "last_check": scheduler.last_check_time
    }, ensure_ascii=False)


def run_scheduler_later():
    """Start scheduler after app starts"""
    time.sleep(5)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scheduler.start())


# Start scheduler in background thread
scheduler_thread = threading.Thread(target=run_scheduler_later, daemon=True)
scheduler_thread.start()

print("✅ Digikala Price Monitor started!")
print("📊 Web interface: http://127.0.0.1:1026")
print("🔄 Checking prices every minute...")

app.listening()