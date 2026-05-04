# simple_test.py
import mysql.connector
from datetime import datetime
import hashlib
import uuid

try:
    # Connect directly to MySQL
    conn = mysql.connector.connect(
        host='localhost',
        database='trading_engine',
        user='trader',
        password='trading123'
    )
    
    cursor = conn.cursor()
    
    # Check if user table exists
    cursor.execute("SHOW TABLES LIKE 'user'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ User table exists")
        
        # Try to insert a test user
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        test_hash = hashlib.sha256("test123".encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO `user` (user_id, username, email, password_hash, amount, crypto_balance, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (test_id, "testuser", "test@test.com", test_hash, 10000, 1, datetime.now()))
        
        conn.commit()
        print("✅ Database insert successful!")
        
        # Verify the insert
        cursor.execute("SELECT user_id, username, email FROM `user` WHERE username = 'testuser'")
        user = cursor.fetchone()
        print(f"✅ User found: {user}")
        
    else:
        print("❌ User table does not exist! Run er_database.py first")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")