import asyncio
from datetime import datetime

class PriceScheduler:
    """Schedules periodic price checks"""
    
    def __init__(self, database, scraper, notifier, check_interval: int = 60):
        """
        Initialize scheduler
        
        Args:
            database: PriceDatabase instance
            scraper: DigikalaScraper instance
            notifier: EmailNotifier instance
            check_interval: Seconds between checks (default: 60 = 1 minute)
        """
        self.db = database
        self.scraper = scraper
        self.notifier = notifier
        self.check_interval = check_interval
        self.last_check_time = None
        self.is_running = False
    
    async def start(self):
        """Start the scheduler loop"""
        self.is_running = True
        print(f"🔄 Scheduler started. Checking every {self.check_interval} seconds...")
        
        while self.is_running:
            await self.check_all_products()
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        print("⏹️ Scheduler stopped")
    
    async def check_all_products(self):
        """Check prices for all monitored products"""
        self.last_check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n⏰ [{self.last_check_time}] Starting price check...")
        
        products = self.db.get_all_products()
        if not products:
            print("ℹ️ No products to check")
            return
        
        for product in products:
            await self._check_product(product)
        
        print(f"✅ Price check completed for {len(products)} products\n")
    
    async def _check_product(self, product: dict):
        """Check price for a single product"""
        try:
            url = product['url']
            name = product['name']
            
            print(f"🔍 Checking: {name}")
            
            # Use await because scraper is now async
            product_info = await self.scraper.scrape_product(url)
            
            if not product_info:
                print(f"⚠️ Failed to scrape: {name}")
                return
            
            new_price = product_info['price']
            
            # Update database and check for price drop
            price_drop_info = self.db.update_price(url, new_price)
            
            if price_drop_info:
                print(f"📉 Price dropped: {name}")
                print(f"   Old: {price_drop_info['old_price']:,} → New: {price_drop_info['new_price']:,}")
                self.notifier.send_price_drop_notification(price_drop_info)
            else:
                print(f"✓ No price change: {name} ({new_price:,} تومان)")
            
            await asyncio.sleep(1)
        
        except Exception as e:
            print(f"❌ Error checking {product['name']}: {e}")


# Example usage for standalone testing
if __name__ == "__main__":
    import asyncio
    from price_monitor.database import PriceDatabase
    from price_monitor.scraper import DigikalaScraper
    from price_monitor.notifier import EmailNotifier

    db = PriceDatabase()
    scraper = DigikalaScraper()
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="your-email@gmail.com",
        sender_password="your-app-password",
        recipient_email="your-email@gmail.com"
    )

    scheduler = PriceScheduler(db, scraper, notifier, check_interval=60)
    asyncio.run(scheduler.start())
