import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class PriceDatabase:
    """Manages SQLite database for price history"""
    
    def __init__(self, db_path: str = "prices.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                current_price INTEGER NOT NULL,
                lowest_price INTEGER NOT NULL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, url: str, name: str, price: int) -> bool:
        """Add a new product to monitor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            
            cursor.execute('''
                INSERT INTO products (url, name, current_price, lowest_price, last_checked)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, name, price, price, now))
            
            product_id = cursor.lastrowid
            
            # Add to history
            cursor.execute('''
                INSERT INTO price_history (product_id, price)
                VALUES (?, ?)
            ''', (product_id, price))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added product: {name}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️ Product already exists: {url}")
            return False
        except Exception as e:
            print(f"❌ Error adding product: {e}")
            return False
    
    def update_price(self, url: str, new_price: int) -> Optional[Dict]:
        """
        Update product price and return info if price dropped
        
        Returns:
            Dict with product info if price dropped, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current product info
        cursor.execute('''
            SELECT id, name, current_price, lowest_price
            FROM products WHERE url = ?
        ''', (url,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        product_id, name, old_price, lowest_price = result
        now = datetime.now()
        
        # Update product
        new_lowest = min(new_price, lowest_price)
        cursor.execute('''
            UPDATE products
            SET current_price = ?, lowest_price = ?, last_checked = ?
            WHERE id = ?
        ''', (new_price, new_lowest, now, product_id))
        
        # Add to history
        cursor.execute('''
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
        ''', (product_id, new_price))
        
        conn.commit()
        conn.close()
        
        # Check if price dropped
        if new_price < old_price:
            price_drop = old_price - new_price
            drop_percentage = (price_drop / old_price) * 100
            
            return {
                'name': name,
                'url': url,
                'old_price': old_price,
                'new_price': new_price,
                'price_drop': price_drop,
                'drop_percentage': drop_percentage
            }
        
        return None
    
    def get_all_products(self) -> List[Dict]:
        """Get all monitored products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, name, current_price, lowest_price, last_checked
            FROM products
            ORDER BY last_checked DESC
        ''')
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'url': row[0],
                'name': row[1],
                'current_price': row[2],
                'lowest_price': row[3],
                'last_checked': row[4] if row[4] else 'هرگز'
            })
        
        conn.close()
        return products
    
    def get_price_history(self, url: str, limit: int = 10) -> List[Dict]:
        """Get price history for a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ph.price, ph.checked_at
            FROM price_history ph
            JOIN products p ON ph.product_id = p.id
            WHERE p.url = ?
            ORDER BY ph.checked_at DESC
            LIMIT ?
        ''', (url, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'price': row[0],
                'checked_at': row[1]
            })
        
        conn.close()
        return history
    
    def remove_product(self, url: str) -> bool:
        """Remove a product from monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM products WHERE url = ?', (url,))
            
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"❌ Error removing product: {e}")
            return False