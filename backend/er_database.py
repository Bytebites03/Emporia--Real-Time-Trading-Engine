"""
Complete ER Database - 9 Tables with All Relationships
Tables are created only ONCE, data persists across restarts
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
import uuid
from typing import Dict, List, Optional, Any

class ERDatabase:
    """ER Database with 9 tables and all relationships"""
    
    def __init__(self):
        self.connection = None
        self.connect()
        self.init_database()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='trading_engine',
                user='trader',
                password='trading123',
                autocommit=True
            )
            print("✅ ER Database connected!")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return cursor"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor
        except Error as e:
            print(f"⚠️ Query warning: {e}")
            return None
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        cursor = self.execute_query("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_schema = 'trading_engine' AND table_name = %s
        """, (table_name,))
        if cursor:
            result = cursor.fetchone()
            return result['count'] > 0
        return False
    
    def init_database(self):
        """Initialize all 9 tables ONLY IF they don't exist"""
        
        print("📊 Checking ER Database tables...")
        print("=" * 60)
        
        # Check if tables already exist
        if self.table_exists('user'):
            print("✅ Tables already exist! Skipping creation.")
            print("   (Your existing data is preserved)")
            return
        
        print("🔄 Creating tables for the first time...")
        
        # =====================================================
        # TABLE 1: USER
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS `user` (
                user_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                amount DECIMAL(20, 8) DEFAULT 10000.0,
                crypto_balance DECIMAL(20, 8) DEFAULT 1.0,
                dob DATE,
                age INT DEFAULT 0,
                notification_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 1: 'user' created")
        
        # =====================================================
        # TABLE 2: PAYMENT
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS payment (
                payment_id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                subtype ENUM('deposit', 'withdrawal') NOT NULL,
                status VARCHAR(20) DEFAULT 'completed',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 2: 'payment' created")
        
        # =====================================================
        # TABLE 3: DEPOSIT
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS deposit (
                deposit_id VARCHAR(50) PRIMARY KEY,
                payment_id VARCHAR(50) NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                net_id VARCHAR(100),
                amount DECIMAL(20, 8) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'completed',
                INDEX idx_payment (payment_id),
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 3: 'deposit' created")
        
        # =====================================================
        # TABLE 4: WITHDRAWAL
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS withdrawal (
                withdrawal_id VARCHAR(50) PRIMARY KEY,
                payment_id VARCHAR(50) NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                net_id VARCHAR(100),
                amount DECIMAL(20, 8) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                INDEX idx_payment (payment_id),
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 4: 'withdrawal' created")
        
        # =====================================================
        # TABLE 5: TRADING ACCOUNT
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS trading_account (
                account_id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                account_name VARCHAR(100) DEFAULT 'Main Account',
                balance DECIMAL(20, 8) DEFAULT 10000.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 5: 'trading_account' created")
        
        # =====================================================
        # TABLE 6: INSTRUMENT
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS instrument (
                instrument_id VARCHAR(50) PRIMARY KEY,
                ticker_symbol VARCHAR(20) UNIQUE NOT NULL,
                instrument_name VARCHAR(100) NOT NULL,
                exchange VARCHAR(50) NOT NULL,
                instrument_type VARCHAR(20) DEFAULT 'crypto',
                current_price DECIMAL(20, 8) DEFAULT 50000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol (ticker_symbol),
                INDEX idx_exchange (exchange)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 6: 'instrument' created")
        
        # =====================================================
        # TABLE 7: ORDER
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS `order` (
                order_id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                account_id VARCHAR(50) NOT NULL,
                instrument_id VARCHAR(50) NOT NULL,
                status ENUM('buy', 'sell') NOT NULL,
                order_type ENUM('market', 'limit') NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                filled_quantity DECIMAL(20, 8) DEFAULT 0,
                price DECIMAL(20, 8),
                exchange VARCHAR(50),
                order_status VARCHAR(20) DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_account (account_id),
                INDEX idx_instrument (instrument_id),
                INDEX idx_status (order_status),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 7: 'order' created")
        
        # =====================================================
        # TABLE 8: MARKET DATA
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS market_data (
                data_id VARCHAR(50) PRIMARY KEY,
                instrument_id VARCHAR(50) NOT NULL,
                price_history DECIMAL(20, 8) NOT NULL,
                volume_traded DECIMAL(20, 8) DEFAULT 0,
                bid_price DECIMAL(20, 8),
                ask_price DECIMAL(20, 8),
                log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_instrument (instrument_id),
                INDEX idx_log_time (log_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 8: 'market_data' created")
        
        # =====================================================
        # TABLE 9: TRADE
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS trade (
                trade_id VARCHAR(50) PRIMARY KEY,
                instrument_id VARCHAR(50) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                total_value DECIMAL(20, 8) NOT NULL,
                buyer_id VARCHAR(50) NOT NULL,
                seller_id VARCHAR(50) NOT NULL,
                fee DECIMAL(20, 8) DEFAULT 0,
                profit_or_loss DECIMAL(20, 8) DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                market_data_id VARCHAR(50),
                INDEX idx_instrument (instrument_id),
                INDEX idx_buyer (buyer_id),
                INDEX idx_seller (seller_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 9: 'trade' created")
        
        # =====================================================
        # JUNCTION TABLE 1: ORDER_TRADE_MAPPING (M:N)
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS order_trade_mapping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                trade_id VARCHAR(50) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                INDEX idx_order (order_id),
                INDEX idx_trade (trade_id),
                UNIQUE KEY unique_order_trade (order_id, trade_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Junction Table: 'order_trade_mapping' created")
        
        # =====================================================
        # JUNCTION TABLE 2: TRADING_ACCOUNT_INSTRUMENT (M:N)
        # =====================================================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS trading_account_instrument (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_id VARCHAR(50) NOT NULL,
                instrument_id VARCHAR(50) NOT NULL,
                quantity DECIMAL(20, 8) DEFAULT 0,
                average_entry_price DECIMAL(20, 8) DEFAULT 0,
                current_pnl DECIMAL(20, 8) DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_account_instrument (account_id, instrument_id),
                INDEX idx_account (account_id),
                INDEX idx_instrument (instrument_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Junction Table: 'trading_account_instrument' created")
        
        # Add foreign keys after tables are created
        print("\n🔗 Adding foreign key constraints...")
        self.add_foreign_keys()
        
        # Insert default data only if tables are empty
        self.insert_default_instruments()
        self.create_default_users()
        
        print("\n" + "=" * 60)
        print("✅ ALL TABLES CREATED SUCCESSFULLY!")
        print("=" * 60)
    
    def add_foreign_keys(self):
        """Add foreign key constraints"""
        
        # Payment foreign key
        self.execute_query("""
            ALTER TABLE payment ADD CONSTRAINT IF NOT EXISTS fk_payment_user 
            FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        
        # Deposit foreign keys
        self.execute_query("""
            ALTER TABLE deposit ADD CONSTRAINT IF NOT EXISTS fk_deposit_payment 
            FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE deposit ADD CONSTRAINT IF NOT EXISTS fk_deposit_user 
            FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        
        # Withdrawal foreign keys
        self.execute_query("""
            ALTER TABLE withdrawal ADD CONSTRAINT IF NOT EXISTS fk_withdrawal_payment 
            FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE withdrawal ADD CONSTRAINT IF NOT EXISTS fk_withdrawal_user 
            FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        
        # Trading account foreign key
        self.execute_query("""
            ALTER TABLE trading_account ADD CONSTRAINT IF NOT EXISTS fk_trading_account_user 
            FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        
        # Order foreign keys
        self.execute_query("""
            ALTER TABLE `order` ADD CONSTRAINT IF NOT EXISTS fk_order_user 
            FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE `order` ADD CONSTRAINT IF NOT EXISTS fk_order_account 
            FOREIGN KEY (account_id) REFERENCES trading_account(account_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE `order` ADD CONSTRAINT IF NOT EXISTS fk_order_instrument 
            FOREIGN KEY (instrument_id) REFERENCES instrument(instrument_id) ON DELETE CASCADE
        """)
        
        # Market data foreign key
        self.execute_query("""
            ALTER TABLE market_data ADD CONSTRAINT IF NOT EXISTS fk_market_data_instrument 
            FOREIGN KEY (instrument_id) REFERENCES instrument(instrument_id) ON DELETE CASCADE
        """)
        
        # Trade foreign keys
        self.execute_query("""
            ALTER TABLE trade ADD CONSTRAINT IF NOT EXISTS fk_trade_instrument 
            FOREIGN KEY (instrument_id) REFERENCES instrument(instrument_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE trade ADD CONSTRAINT IF NOT EXISTS fk_trade_buyer 
            FOREIGN KEY (buyer_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE trade ADD CONSTRAINT IF NOT EXISTS fk_trade_seller 
            FOREIGN KEY (seller_id) REFERENCES `user`(user_id) ON DELETE CASCADE
        """)
        
        # Junction table foreign keys
        self.execute_query("""
            ALTER TABLE order_trade_mapping ADD CONSTRAINT IF NOT EXISTS fk_otm_order 
            FOREIGN KEY (order_id) REFERENCES `order`(order_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE order_trade_mapping ADD CONSTRAINT IF NOT EXISTS fk_otm_trade 
            FOREIGN KEY (trade_id) REFERENCES trade(trade_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE trading_account_instrument ADD CONSTRAINT IF NOT EXISTS fk_tai_account 
            FOREIGN KEY (account_id) REFERENCES trading_account(account_id) ON DELETE CASCADE
        """)
        self.execute_query("""
            ALTER TABLE trading_account_instrument ADD CONSTRAINT IF NOT EXISTS fk_tai_instrument 
            FOREIGN KEY (instrument_id) REFERENCES instrument(instrument_id) ON DELETE CASCADE
        """)
        
        print("✅ Foreign key constraints added")
    
    def insert_default_instruments(self):
        """Insert default trading instruments only if table is empty"""
        cursor = self.execute_query("SELECT COUNT(*) as count FROM instrument")
        if cursor:
            result = cursor.fetchone()
            if result['count'] == 0:
                instruments = [
                    ("inst_btc", "BTC/USD", "Bitcoin", "Binance", "crypto", 50000),
                    ("inst_eth", "ETH/USD", "Ethereum", "Binance", "crypto", 3000),
                ]
                for inst in instruments:
                    self.execute_query("""
                        INSERT IGNORE INTO instrument (instrument_id, ticker_symbol, instrument_name, exchange, instrument_type, current_price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, inst)
                print("✅ Default instruments inserted")
    
    def create_default_users(self):
        """Create default admin and demo users only if no users exist"""
        cursor = self.execute_query("SELECT COUNT(*) as count FROM `user`")
        if cursor:
            result = cursor.fetchone()
            if result['count'] == 0:
                # Create admin user
                admin_id = f"user_{uuid.uuid4().hex[:8]}"
                admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
                
                self.execute_query("""
                    INSERT INTO `user` (user_id, first_name, last_name, username, email, password_hash, amount, crypto_balance, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (admin_id, "Admin", "User", "admin", "admin@trading.com", admin_hash, 100000.0, 10.0, datetime.now()))
                
                # Create trading account for admin
                admin_account_id = f"acc_{uuid.uuid4().hex[:8]}"
                self.execute_query("""
                    INSERT INTO trading_account (account_id, user_id, account_name, balance, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (admin_account_id, admin_id, "Main Account", 100000.0, datetime.now()))
                
                print("✅ Created admin user: admin / admin123")
                
                # Create demo user
                demo_id = f"user_{uuid.uuid4().hex[:8]}"
                demo_hash = hashlib.sha256("demo123".encode()).hexdigest()
                
                self.execute_query("""
                    INSERT INTO `user` (user_id, first_name, last_name, username, email, password_hash, amount, crypto_balance, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (demo_id, "Demo", "User", "demo", "demo@trading.com", demo_hash, 10000.0, 1.0, datetime.now()))
                
                # Create trading account for demo
                demo_account_id = f"acc_{uuid.uuid4().hex[:8]}"
                self.execute_query("""
                    INSERT INTO trading_account (account_id, user_id, account_name, balance, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (demo_account_id, demo_id, "Main Account", 10000.0, datetime.now()))
                
                print("✅ Created demo user: demo / demo123")
    
    # ========== USER OPERATIONS ==========
    
    def get_user(self, username: str = None, email: str = None, user_id: str = None):
        """Get user from database"""
        if username:
            cursor = self.execute_query("SELECT * FROM `user` WHERE username = %s", (username,))
        elif email:
            cursor = self.execute_query("SELECT * FROM `user` WHERE email = %s", (email,))
        elif user_id:
            cursor = self.execute_query("SELECT * FROM `user` WHERE user_id = %s", (user_id,))
        else:
            return None
        
        if cursor:
            return cursor.fetchone()
        return None
    
    def get_all_users(self):
        """Get all users"""
        cursor = self.execute_query("SELECT * FROM `user` ORDER BY created_at DESC")
        if cursor:
            return cursor.fetchall()
        return []
def execute_query(self, query: str, params: tuple = None):
    """Execute a query and return cursor"""
    try:
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        self.connection.commit()  # Make sure to commit!
        return cursor
    except Error as e:
        print(f"Query error: {e}")
        return None
# Create global instance
db = ERDatabase()