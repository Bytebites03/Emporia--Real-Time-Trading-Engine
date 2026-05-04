from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List
import asyncio
import uuid
import hashlib
import random
from datetime import datetime
from contextlib import asynccontextmanager

# Import your modules
from er_database import db
from matching_engine import MatchingEngine
from chatbot import FinanceTutor
from profit_predictor import predictor

# ==================== INITIALIZATION ====================
engine = MatchingEngine(symbol="BTC/USD")
chatbot = FinanceTutor()
TOKENS = {}
RECENT_TRADES = []

# Live prices for all instruments
live_prices = {
    "BTC/USD": 50000,
    "ETH/USD": 3000,
    "AAPL": 175.34,
    "GOOGL": 140.56,
    "MSFT": 380.23,
    "TSLA": 180.45,
    "AMZN": 145.78,
    "META": 310.20,
    "NVDA": 800.50,
    "XAU/USD": 2000.50,
    "XAG/USD": 25.30,
    "EUR/USD": 1.0850,
    "GBP/USD": 1.2530,
}

# ==================== WEBSOCKET MANAGER ====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ==================== LIFESPAN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("🚀 STARTING TRADING ENGINE SERVER")
    print("=" * 60)
    print("📍 Backend: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("\n📝 Demo Accounts:")
    print("   - Username: admin / Password: admin123")
    print("   - Username: demo / Password: demo123")
    print("=" * 60)
    
    asyncio.create_task(simulate_market_data())
    asyncio.create_task(broadcast_orderbook_periodically())
    
    yield
    
    print("🛑 Shutting down...")

# ==================== FASTAPI APP ====================
app = FastAPI(title="Trading Engine API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ==================== REQUEST MODELS ====================
class OrderRequest(BaseModel):
    side: str
    type: str
    symbol: str = "BTC/USD"
    price: float = 0.0
    quantity: float

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    username: str
    password: str

# ==================== AUTH HELPER ====================
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = TOKENS[token]
    cursor = db.execute_query("SELECT * FROM `user` WHERE user_id = %s", (user_id,))
    user = cursor.fetchone() if cursor else None
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user['id'] = user['user_id']
    return user

# ==================== AUTH ENDPOINTS ====================
@app.post("/auth/register")
async def register_user(user_data: UserRegister):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    cursor = db.execute_query("SELECT * FROM `user` WHERE username = %s", (user_data.username,))
    if cursor and cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    cursor = db.execute_query("SELECT * FROM `user` WHERE email = %s", (user_data.email,))
    if cursor and cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
    
    db.execute_query("""
        INSERT INTO `user` (user_id, username, email, password_hash, amount, crypto_balance, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, user_data.username, user_data.email, password_hash, 10000.0, 1.0, datetime.now()))
    
    account_id = f"acc_{uuid.uuid4().hex[:8]}"
    db.execute_query("""
        INSERT INTO trading_account (account_id, user_id, account_name, balance, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (account_id, user_id, "Main Account", 10000.0, datetime.now()))
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "cash_balance": 10000.0,
            "crypto_balance": 1.0
        }
    }

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    cursor = db.execute_query("SELECT * FROM `user` WHERE username = %s", (login_data.username,))
    user = cursor.fetchone() if cursor else None
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    password_hash = hashlib.sha256(login_data.password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    db.execute_query("UPDATE `user` SET last_login = %s WHERE user_id = %s", (datetime.now(), user['user_id']))
    
    token = str(uuid.uuid4())
    TOKENS[token] = user['user_id']
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user['username'],
        "user_id": user['user_id'],
        "cash_balance": float(user['amount']),
        "crypto_balance": float(user['crypto_balance'])
    }

@app.get("/auth/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = TOKENS[token]
    cursor = db.execute_query("SELECT * FROM `user` WHERE user_id = %s", (user_id,))
    user = cursor.fetchone() if cursor else None
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user['user_id'],
        "username": user['username'],
        "email": user['email'],
        "cash_balance": float(user['amount']),
        "crypto_balance": float(user['crypto_balance'])
    }

# ==================== PORTFOLIO ====================
@app.get("/portfolio")
async def get_portfolio(current_user = Depends(get_current_user)):
    # Get current price of BTC (or first instrument)
    btc_price = live_prices.get("BTC/USD", 50000)
    return {
        "cash": float(current_user['amount']),
        "crypto": float(current_user['crypto_balance']),
        "total_value": float(current_user['amount']) + (float(current_user['crypto_balance']) * btc_price)
    }

# ==================== ORDER ====================
@app.post("/order")
async def place_order(order_req: OrderRequest, current_user = Depends(get_current_user)):
    global live_prices
    
    user_id = current_user['user_id']
    symbol = order_req.symbol
    
    # Get current live price for this instrument
    current_price = live_prices.get(symbol, 50000)
    
    # For market orders, use current live price
    # For limit orders, use user's specified price
    execution_price = current_price if order_req.type == "market" else order_req.price
    total_value = execution_price * order_req.quantity
    
    print(f"📝 Order: {order_req.side} {order_req.quantity} {symbol} at ${execution_price:,.4f}")
    print(f"   Current {symbol} price: ${current_price:,.4f}")
    
    cursor = db.execute_query("SELECT * FROM `user` WHERE user_id = %s", (user_id,))
    user = cursor.fetchone() if cursor else None
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if order_req.side == "buy":
        if float(user['amount']) < total_value:
            raise HTTPException(status_code=400, detail=f"Insufficient funds. Need ${total_value:,.2f}")
        new_amount = float(user['amount']) - total_value
        new_crypto = float(user['crypto_balance']) + order_req.quantity
    else:
        if float(user['crypto_balance']) < order_req.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient crypto. Need {order_req.quantity} {symbol}")
        new_amount = float(user['amount']) + total_value
        new_crypto = float(user['crypto_balance']) - order_req.quantity
    
    db.execute_query("UPDATE `user` SET amount = %s, crypto_balance = %s WHERE user_id = %s", 
                    (new_amount, new_crypto, user_id))
    
    trade = {
        "id": str(uuid.uuid4()),
        "symbol": symbol,
        "price": execution_price,
        "quantity": order_req.quantity,
        "side": order_req.side,
        "timestamp": datetime.now().timestamp() * 1000
    }
    RECENT_TRADES.insert(0, trade)
    
    while len(RECENT_TRADES) > 100:
        RECENT_TRADES.pop()
    
    await manager.broadcast({
        "type": "order_executed",
        "trade": trade,
        "user_id": user_id
    })
    
    return {
        "success": True,
        "trade": trade,
        "execution_price": execution_price,
        "current_price": current_price,
        "symbol": symbol,
        "new_balances": {"cash": new_amount, "crypto": new_crypto}
    }

# ==================== BACKGROUND TASKS ====================
async def simulate_market_data():
    global live_prices
    
    while True:
        await asyncio.sleep(3)
        
        for symbol in live_prices:
            current = live_prices[symbol]
            
            # Determine volatility based on instrument type
            if symbol in ["BTC/USD", "ETH/USD"]:
                volatility = 0.005
            elif symbol in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"]:
                volatility = 0.003
            elif symbol in ["XAU/USD", "XAG/USD"]:
                volatility = 0.002
            else:
                volatility = 0.001
            
            change_percent = random.uniform(-volatility, volatility)
            change = current * change_percent
            new_price = current + change
            new_price = max(new_price, current * 0.5)
            
            live_prices[symbol] = new_price
        
        await manager.broadcast({
            "type": "market_update",
            "prices": live_prices.copy(),
            "timestamp": datetime.now().isoformat()
        })

async def broadcast_orderbook_periodically():
    while True:
        await asyncio.sleep(5)
        await manager.broadcast({
            "type": "periodic_orderbook",
            "orderbook": engine.get_order_book()
        })

# ==================== INSTRUMENT ENDPOINTS ====================
@app.get("/instruments")
async def get_instruments():
    """Get all available trading instruments"""
    instruments = []
    for symbol, price in live_prices.items():
        # Determine instrument type based on symbol
        if symbol in ["BTC/USD", "ETH/USD"]:
            instrument_type = "crypto"
        elif symbol in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"]:
            instrument_type = "stock"
        elif symbol in ["XAU/USD", "XAG/USD"]:
            instrument_type = "commodity"
        else:
            instrument_type = "forex"
        
        instruments.append({
            "instrument_id": f"inst_{symbol.replace('/', '_')}",
            "ticker_symbol": symbol,
            "instrument_name": symbol,
            "instrument_type": instrument_type,
            "exchange": "Market",
            "current_price": price
        })
    
    return {"instruments": instruments}

@app.get("/instrument/{symbol}")
async def get_instrument(symbol: str):
    """Get specific instrument details"""
    if symbol in live_prices:
        return {
            "ticker_symbol": symbol,
            "current_price": live_prices[symbol],
            "instrument_type": "crypto" if symbol in ["BTC/USD", "ETH/USD"] else "stock"
        }
    raise HTTPException(status_code=404, detail="Instrument not found")

@app.get("/instrument/price/{symbol}")
async def get_instrument_price(symbol: str):
    """Get current price for an instrument"""
    if symbol in live_prices:
        return {"symbol": symbol, "price": live_prices[symbol]}
    return {"symbol": symbol, "price": 0}

# ==================== OTHER ENDPOINTS ====================
@app.get("/")
async def root():
    return {"message": "Trading Engine API", "status": "running"}

@app.get("/orderbook")
async def get_orderbook():
    return engine.get_order_book()

@app.get("/trades")
async def get_trades(limit: int = 50):
    return RECENT_TRADES[:limit]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return chatbot.get_answer(request.message, request.user_id)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

# ==================== WEBSOCKET ====================
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        user = db.get_user(user_id=user_id)
        await websocket.send_json({
            "type": "connection_established",
            "orderbook": engine.get_order_book(),
            "recent_trades": RECENT_TRADES[:20],
            "prices": live_prices,
            "portfolio": {
                "cash": float(user['amount']) if user else 10000,
                "crypto": float(user['crypto_balance']) if user else 1,
            } if user else {}
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket for live price updates"""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "type": "market_update",
                "prices": live_prices.copy(),
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Price WebSocket disconnected")


# Add these to your app.py if missing
# ==================== PROFIT/LOSS PREDICTOR ENDPOINTS ====================

# ==================== PROFIT/LOSS PREDICTOR ENDPOINTS ====================

@app.post("/predict/entry")
async def predict_entry(
    symbol: str,
    entry_price: float,
    quantity: float
):
    """Predict profit/loss - NO AUTHENTICATION NEEDED"""
    try:
        investment = entry_price * quantity
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": 50000,
            "entry_price": entry_price,
            "quantity": quantity,
            "total_investment": round(investment, 2),
            "predictions": {
                "optimistic": {
                    "profit": round(investment * 0.05, 2),
                    "return_percent": 5.0
                },
                "likely": {
                    "profit": round(investment * 0.02, 2),
                    "return_percent": 2.0
                },
                "pessimistic": {
                    "loss": round(investment * 0.03, 2),
                    "loss_percent": 3.0
                }
            },
            "analysis": {
                "trend": "Neutral",
                "probability_of_profit": 55,
                "risk_level": "Medium"
            },
            "recommendation": "CONSIDER"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/predict/risk-reward")
async def calculate_risk_reward(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    quantity: float
):
    """Calculate risk-reward ratio"""
    try:
        risk_amount = abs(entry_price - stop_loss) * quantity
        reward_amount = abs(take_profit - entry_price) * quantity
        ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        if ratio >= 2:
            assessment = "Good"
            recommendation = "ENTRY"
        elif ratio >= 1.5:
            assessment = "Acceptable"
            recommendation = "CONSIDER"
        else:
            assessment = "Poor"
            recommendation = "AVOID"
        
        return {
            "success": True,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "quantity": quantity,
            "risk_amount": round(risk_amount, 2),
            "reward_amount": round(reward_amount, 2),
            "risk_reward_ratio": round(ratio, 2),
            "assessment": assessment,
            "recommendation": recommendation,
            "win_rate_needed": round(100 / (1 + ratio), 1)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/predict/sentiment/{symbol}")
async def get_sentiment(
    symbol: str,
    current_user = Depends(get_current_user)
):
    """Get market sentiment"""
    try:
        current_price = live_prices.get(symbol, 50000)
        
        # Simple sentiment based on price
        if current_price > 51000:
            sentiment = "Bullish"
            score = 70
            action = "Buy"
        elif current_price < 49000:
            sentiment = "Bearish"
            score = 30
            action = "Sell"
        else:
            sentiment = "Neutral"
            score = 50
            action = "Hold"
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "sentiment": sentiment,
            "score": score,
            "action": action,
            "color": "green" if sentiment == "Bullish" else "red" if sentiment == "Bearish" else "gray",
            "metrics": {
                "change_1h": 0,
                "change_24h": 0,
                "momentum": 0
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)