# backend/instrument_manager.py
import uuid
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from er_database import db

class InstrumentManager:
    """Auto-management system for trading instruments"""
    
    def __init__(self):
        self.instruments = {}
        self.price_simulators = {}
        self.category_configs = {}
        self.load_configurations()
        self.load_instruments()
        self.start_all_simulations()
    
    def load_configurations(self):
        """Load instrument categories and configurations"""
        try:
            cursor = db.execute_query("SELECT * FROM instrument_category WHERE is_active = TRUE")
            if cursor:
                categories = cursor.fetchall()
                for cat in categories:
                    self.category_configs[cat['category_name']] = {
                        'volatility': float(cat['volatility']),
                        'min_quantity': float(cat['min_quantity']),
                        'max_quantity': float(cat['max_quantity']),
                        'lot_size': float(cat['lot_size']) if cat['lot_size'] else 0.001
                    }
        except Exception as e:
            print(f"Error loading configurations: {e}")
            # Default configurations
            self.category_configs = {
                'crypto': {'volatility': 0.005, 'min_quantity': 0.001, 'max_quantity': 100, 'lot_size': 0.001},
                'stock': {'volatility': 0.003, 'min_quantity': 1, 'max_quantity': 10000, 'lot_size': 1},
                'commodity': {'volatility': 0.002, 'min_quantity': 0.1, 'max_quantity': 1000, 'lot_size': 0.1},
                'forex': {'volatility': 0.001, 'min_quantity': 0.01, 'max_quantity': 100, 'lot_size': 0.01}
            }
    
    def load_instruments(self):
        """Load all active instruments from database"""
        try:
            cursor = db.execute_query("""
                SELECT i.* FROM instrument i
                WHERE i.is_active = TRUE
            """)
            if cursor:
                instruments = cursor.fetchall()
                for inst in instruments:
                    instrument_type = inst.get('instrument_type', 'crypto')
                    config = self.category_configs.get(instrument_type, self.category_configs['crypto'])
                    
                    self.instruments[inst['ticker_symbol']] = {
                        'instrument_id': inst.get('instrument_id'),
                        'ticker_symbol': inst.get('ticker_symbol'),
                        'instrument_name': inst.get('instrument_name'),
                        'instrument_type': instrument_type,
                        'exchange': inst.get('exchange', 'Unknown'),
                        'current_price': float(inst.get('current_price', 0)),
                        'volatility': config['volatility'],
                        'min_quantity': config['min_quantity'],
                        'max_quantity': config['max_quantity']
                    }
            else:
                # Add default instruments if none exist
                self.add_default_instruments()
        except Exception as e:
            print(f"Error loading instruments: {e}")
            self.add_default_instruments()
    
    def add_default_instruments(self):
        """Add default instruments if database is empty"""
        default_instruments = [
            ('BTC/USD', 'Bitcoin', 'crypto', 'Binance', 50000),
            ('ETH/USD', 'Ethereum', 'crypto', 'Binance', 3000),
            ('SOL/USD', 'Solana', 'crypto', 'Binance', 150),
            ('AAPL', 'Apple Inc.', 'stock', 'NASDAQ', 175.34),
            ('GOOGL', 'Alphabet Inc.', 'stock', 'NASDAQ', 140.56),
            ('MSFT', 'Microsoft', 'stock', 'NASDAQ', 380.23),
            ('AMZN', 'Amazon', 'stock', 'NASDAQ', 145.78),
            ('TSLA', 'Tesla', 'stock', 'NASDAQ', 180.45),
            ('XAU/USD', 'Gold', 'commodity', 'COMEX', 2000.50),
            ('XAG/USD', 'Silver', 'commodity', 'COMEX', 25.30),
            ('EUR/USD', 'Euro/Dollar', 'forex', 'Forex', 1.0850),
            ('GBP/USD', 'Pound/Dollar', 'forex', 'Forex', 1.2530),
        ]
        
        for ticker, name, inst_type, exchange, price in default_instruments:
            instrument_id = f"inst_{uuid.uuid4().hex[:8]}"
            config = self.category_configs.get(inst_type, self.category_configs['crypto'])
            
            try:
                db.execute_query("""
                    INSERT INTO instrument (instrument_id, ticker_symbol, instrument_name, 
                                           instrument_type, exchange, current_price, 
                                           min_quantity, max_quantity, created_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (instrument_id, ticker, name, inst_type, exchange, price,
                      config['min_quantity'], config['max_quantity'], datetime.now(), True))
            except Exception as e:
                print(f"Error adding {ticker}: {e}")
    
    def start_all_simulations(self):
        """Start price simulations for all instruments"""
        for symbol in self.instruments:
            self.start_price_simulation(symbol)
    
    def start_price_simulation(self, symbol: str):
        """Start automatic price simulation for an instrument"""
        async def simulate():
            while True:
                await asyncio.sleep(5)  # Update every 5 seconds
                if symbol in self.instruments:
                    instrument = self.instruments[symbol]
                    current_price = instrument['current_price']
                    instrument_type = instrument['instrument_type']
                    
                    # Different volatility based on instrument type
                    volatility_map = {
                        'crypto': 0.005,   # 0.5% max change
                        'stock': 0.003,    # 0.3% max change
                        'commodity': 0.002, # 0.2% max change
                        'forex': 0.001     # 0.1% max change
                    }
                    volatility = volatility_map.get(instrument_type, 0.003)
                    
                    change_percent = random.uniform(-volatility, volatility)
                    change = current_price * change_percent
                    new_price = max(current_price + change, 0.01)
                    
                    self.update_price(symbol, new_price)
        
        # Run simulation in background
        if symbol in self.price_simulators:
            self.price_simulators[symbol].cancel()
        self.price_simulators[symbol] = asyncio.create_task(simulate())
    
    def add_instrument(self, ticker_symbol: str, instrument_name: str, 
                       instrument_type: str, exchange: str, 
                       initial_price: float, **kwargs) -> Dict:
        """Add a new instrument dynamically"""
        try:
            # Generate unique instrument ID
            instrument_id = f"inst_{uuid.uuid4().hex[:8]}"
            
            # Get category configuration
            category_config = self.category_configs.get(instrument_type, self.category_configs['crypto'])
            
            # Insert into instrument table
            db.execute_query("""
                INSERT INTO instrument (
                    instrument_id, ticker_symbol, instrument_name, 
                    instrument_type, exchange, current_price, 
                    min_quantity, max_quantity, created_at, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                instrument_id, ticker_symbol.upper(), instrument_name,
                instrument_type, exchange, initial_price,
                category_config['min_quantity'], category_config['max_quantity'],
                datetime.now(), True
            ))
            
            # Add to local cache
            self.instruments[ticker_symbol.upper()] = {
                'instrument_id': instrument_id,
                'ticker_symbol': ticker_symbol.upper(),
                'instrument_name': instrument_name,
                'instrument_type': instrument_type,
                'exchange': exchange,
                'current_price': initial_price,
                'volatility': category_config['volatility'],
                'min_quantity': category_config['min_quantity'],
                'max_quantity': category_config['max_quantity']
            }
            
            # Start price simulation for this instrument
            self.start_price_simulation(ticker_symbol.upper())
            
            print(f"✅ New instrument added: {ticker_symbol.upper()} - {instrument_name}")
            
            return {
                'success': True,
                'instrument': self.instruments[ticker_symbol.upper()],
                'message': f'Instrument {ticker_symbol} added successfully'
            }
            
        except Exception as e:
            print(f"❌ Error adding instrument: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_instrument(self, ticker_symbol: str) -> Dict:
        """Remove an instrument (soft delete)"""
        try:
            db.execute_query("""
                UPDATE instrument SET is_active = FALSE 
                WHERE ticker_symbol = %s
            """, (ticker_symbol.upper(),))
            
            # Stop price simulation
            if ticker_symbol.upper() in self.price_simulators:
                self.price_simulators[ticker_symbol.upper()].cancel()
                del self.price_simulators[ticker_symbol.upper()]
            
            # Remove from cache
            if ticker_symbol.upper() in self.instruments:
                del self.instruments[ticker_symbol.upper()]
            
            return {'success': True, 'message': f'Instrument {ticker_symbol} removed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_price(self, symbol: str, new_price: float):
        """Update instrument price"""
        if symbol in self.instruments:
            self.instruments[symbol]['current_price'] = new_price
            
            # Update database
            db.execute_query("""
                UPDATE instrument SET current_price = %s, updated_at = %s
                WHERE ticker_symbol = %s
            """, (new_price, datetime.now(), symbol))
    
    def get_all_instruments(self) -> List[Dict]:
        """Get all active instruments"""
        return list(self.instruments.values())
    
    def get_instrument(self, symbol: str) -> Optional[Dict]:
        """Get specific instrument by symbol"""
        return self.instruments.get(symbol.upper())
    
    def get_price(self, symbol: str) -> float:
        """Get current price of instrument"""
        if symbol.upper() in self.instruments:
            return self.instruments[symbol.upper()]['current_price']
        return 0
    
    def get_instruments_by_type(self, instrument_type: str) -> List[Dict]:
        """Get instruments filtered by type"""
        return [inst for inst in self.instruments.values() 
                if inst['instrument_type'] == instrument_type]
    
    def get_instrument_types(self) -> List[str]:
        """Get all available instrument types"""
        return list(set(inst['instrument_type'] for inst in self.instruments.values()))

# Create global instance
instrument_manager = InstrumentManager()