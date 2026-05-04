# add_instruments.py
from er_database import db
import uuid
from datetime import datetime

def add_instrument(ticker, name, inst_type, exchange, price):
    """Add instrument directly to database"""
    instrument_id = f"inst_{uuid.uuid4().hex[:8]}"
    
    result = db.execute_query("""
        INSERT INTO instrument (instrument_id, ticker_symbol, instrument_name, instrument_type, exchange, current_price, created_at, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (instrument_id, ticker, name, inst_type, exchange, price, datetime.now(), 1))
    
    print(f"Added: {ticker} - {name}")

# Add sample instruments
instruments_to_add = [
    ("BTC/USD", "Bitcoin", "crypto", "Binance", 50000),
    ("ETH/USD", "Ethereum", "crypto", "Binance", 3000),
    ("SOL/USD", "Solana", "crypto", "Binance", 150),
    ("AAPL", "Apple Inc.", "stock", "NASDAQ", 175.34),
    ("GOOGL", "Alphabet Inc.", "stock", "NASDAQ", 140.56),
    ("MSFT", "Microsoft", "stock", "NASDAQ", 380.23),
    ("AMZN", "Amazon", "stock", "NASDAQ", 145.78),
    ("TSLA", "Tesla", "stock", "NASDAQ", 180.45),
    ("META", "Meta", "stock", "NASDAQ", 310.20),
    ("NVDA", "NVIDIA", "stock", "NASDAQ", 800.50),
    ("XAU/USD", "Gold", "commodity", "COMEX", 2000.50),
    ("XAG/USD", "Silver", "commodity", "COMEX", 25.30),
    ("EUR/USD", "Euro/Dollar", "forex", "Forex", 1.0850),
    ("GBP/USD", "Pound/Dollar", "forex", "Forex", 1.2530),
]

print("Adding instruments to database...")
for ticker, name, inst_type, exchange, price in instruments_to_add:
    add_instrument(ticker, name, inst_type, exchange, price)

print("\n✅ All instruments added!")

# Verify
print("\nVerifying...")
cursor = db.execute_query("SELECT ticker_symbol, instrument_name, instrument_type FROM instrument WHERE is_active = 1")
if cursor:
    instruments = cursor.fetchall()
    print(f"Total instruments in database: {len(instruments)}")
    for inst in instruments:
        print(f"  - {inst['ticker_symbol']}: {inst['instrument_name']} ({inst['instrument_type']})")