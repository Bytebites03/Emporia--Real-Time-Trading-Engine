# backend/instrument_service.py
import random
import asyncio
from datetime import datetime
from typing import Dict, Any
from er_database import db

class InstrumentService:
    """Manages live prices for all instruments"""
    
    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.price_history: Dict[str, list] = {}
        self.subscribers: Dict[str, list] = {}
        self.load_initial_prices()
    
    def load_initial_prices(self):
        """Load current prices from database"""
        cursor = db.execute_query("SELECT instrument_id, ticker_symbol, current_price FROM instrument")
        if cursor:
            instruments = cursor.fetchall()
            for inst in instruments:
                self.prices[inst['ticker_symbol']] = float(inst['current_price'])
                self.price_history[inst['ticker_symbol']] = []
                self.subscribers[inst['ticker_symbol']] = []
    
    def get_price(self, symbol: str) -> float:
        """Get current price for instrument"""
        return self.prices.get(symbol, 0)
    
    def update_price(self, symbol: str, new_price: float):
        """Update price for instrument"""
        old_price = self.prices.get(symbol, new_price)
        self.prices[symbol] = new_price
        change = new_price - old_price
        change_percent = (change / old_price) * 100 if old_price > 0 else 0
        
        # Store price history
        self.price_history[symbol].append({
            'price': new_price,
            'timestamp': datetime.now().isoformat(),
            'change': change,
            'change_percent': change_percent
        })
        
        # Keep last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol].pop(0)
        
        # Update database
        db.execute_query("""
            UPDATE instrument SET current_price = %s, updated_at = %s 
            WHERE ticker_symbol = %s
        """, (new_price, datetime.now(), symbol))
        
        # Record price history
        cursor = db.execute_query("SELECT instrument_id FROM instrument WHERE ticker_symbol = %s", (symbol,))
        if cursor:
            instrument = cursor.fetchone()
            if instrument:
                db.execute_query("""
                    INSERT INTO price_history (instrument_id, price, timestamp)
                    VALUES (%s, %s, %s)
                """, (instrument['instrument_id'], new_price, datetime.now()))
        
        return {'price': new_price, 'change': change, 'change_percent': change_percent}
    
    def simulate_price_change(self, symbol: str):
        """Simulate random price movement for an instrument"""
        current_price = self.get_price(symbol)
        if current_price <= 0:
            return
        
        # Different volatility based on instrument type
        cursor = db.execute_query("SELECT instrument_type FROM instrument WHERE ticker_symbol = %s", (symbol,))
        instrument_type = 'crypto'
        if cursor:
            inst = cursor.fetchone()
            if inst:
                instrument_type = inst['instrument_type']
        
        # Set volatility based on instrument type
        volatility = {
            'crypto': 0.02,    # 2% max change
            'stock': 0.01,     # 1% max change
            'commodity': 0.005, # 0.5% max change
            'forex': 0.002     # 0.2% max change
        }.get(instrument_type, 0.01)
        
        change_percent = random.uniform(-volatility, volatility)
        change = current_price * change_percent
        new_price = current_price + change
        
        # Ensure price doesn't go negative
        new_price = max(new_price, current_price * 0.5)
        
        return self.update_price(symbol, new_price)
    
    def subscribe(self, symbol: str, callback):
        """Subscribe to price updates for an instrument"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)
    
    def unsubscribe(self, symbol: str, callback):
        """Unsubscribe from price updates"""
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
    
    def broadcast_price(self, symbol: str):
        """Broadcast price update to all subscribers"""
        price_data = {
            'symbol': symbol,
            'price': self.get_price(symbol),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get change info
        if self.price_history[symbol] and len(self.price_history[symbol]) > 1:
            last = self.price_history[symbol][-1]
            price_data['change'] = last.get('change', 0)
            price_data['change_percent'] = last.get('change_percent', 0)
        
        for callback in self.subscribers.get(symbol, []):
            try:
                callback(price_data)
            except Exception as e:
                print(f"Error broadcasting to subscriber: {e}")

# Create global instance
instrument_service = InstrumentService()

# Start price simulation for all instruments
async def start_price_simulation():
    """Simulate price changes for all instruments"""
    cursor = db.execute_query("SELECT ticker_symbol FROM instrument")
    if cursor:
        instruments = cursor.fetchall()
        while True:
            for inst in instruments:
                instrument_service.simulate_price_change(inst['ticker_symbol'])
                await asyncio.sleep(0.5)  # Different stagger
            await asyncio.sleep(2)  # Update every 2 seconds per instrument