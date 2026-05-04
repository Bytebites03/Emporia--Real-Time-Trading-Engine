"""
Advanced Finance Tutor Chatbot Module for Trading Engine
Educational chatbot that teaches trading concepts and app usage
"""

import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class FinanceTutor:
    """Advanced educational chatbot for trading concepts and app tutorials"""
    
    def __init__(self):
        """Initialize the finance tutor with knowledge base"""
        
        # Track conversation history for each user
        self.conversation_history: Dict[str, List[Dict]] = {}
        
        # Track user skill levels (beginner, intermediate, advanced)
        self.user_skill_levels: Dict[str, str] = {}
        
        # Track user interests for personalized recommendations
        self.user_interests: Dict[str, List[str]] = {}
        
        # Comprehensive knowledge base
        self.knowledge_base = {
            # ==================== BASIC CONCEPTS ====================
            "what is a limit order": {
                "answer": """📚 **Limit Order Explained**

A **Limit Order** lets you buy or sell at a specific price or better.

**How it works:**
- 🟢 **Buy Limit**: Set maximum price you'll pay (e.g., buy BTC @ $45,000)
- 🔴 **Sell Limit**: Set minimum price you'll accept (e.g., sell BTC @ $55,000)

**Example:** 
You want to buy Bitcoin at $45,000. Current price is $50,000. Your limit order sits in the order book until price drops to $45,000, then executes automatically.

**Pros:** Price control, no slippage
**Cons:** May never execute if price doesn't reach your limit

**In our app:** Select "Limit Order" and enter your desired price.""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            "what is a market order": {
                "answer": """📚 **Market Order Explained**

A **Market Order** buys or sells immediately at the best available price.

**How it works:**
- Instant execution (milliseconds)
- Matches with existing orders in the book

**Example:** 
Bitcoin is trading at $50,000 (bid) / $50,100 (ask). You place a market buy order and immediately get filled at $50,100.

**Pros:** Guaranteed execution, fast
**Cons:** Price uncertainty, possible slippage

**In our app:** Select "Market Order" - no price entry needed!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            "what is order book": {
                "answer": """📚 **Order Book Explained**

The **Order Book** shows all pending buy and sell orders.

**Two sides:**
- 🟢 **Bids (Buy orders)** - Highest price on top (green)
- 🔴 **Asks (Sell orders)** - Lowest price on top (red)

**Key terms:**
- **Best Bid**: Highest price someone will buy at
- **Best Ask**: Lowest price someone will sell at  
- **Spread**: Difference between best bid and ask

**In our app:** Bids on left (green), asks on right (red)!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            "what is spread": {
                "answer": """📚 **Bid-Ask Spread Explained**

The **Spread** is the difference between highest buy order and lowest sell order.

**Formula:** Spread = Best Ask - Best Bid

**Example:**
- Best Bid: $49,900
- Best Ask: $50,100  
- Spread: $200 (0.4%)

**What it means:**
- **Narrow spread** = High liquidity
- **Wide spread** = Low liquidity, higher costs

**In our app:** Spread is displayed between bids and asks!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            # ==================== INTERMEDIATE CONCEPTS ====================
            "how to read candlestick chart": {
                "answer": """📊 **Candlestick Chart Guide**

Each candlestick shows 4 key prices: Open, High, Low, Close.

**Colors:**
- 🟢 **Green candle** = Close > Open (price up)
- 🔴 **Red candle** = Close < Open (price down)

**Common patterns:**
- **Long wick** = Rejection at that price level
- **Small body** = Indecision in market
- **Doji** = Open = Close, potential reversal

**In our app:** The price chart updates in real-time with each trade!""",
                "category": "analysis",
                "difficulty": "intermediate"
            },
            
            "what is liquidity": {
                "answer": """💧 **Liquidity Explained**

**Liquidity** = How easily you can buy/sell without affecting price.

**High liquidity means:**
- Many active traders
- Tight spreads
- Large orders execute without slippage

**Low liquidity means:**
- Fewer participants
- Wide spreads
- Your order might move price

**Check liquidity in our app:**
1. Look at order book depth
2. Check spread size
3. Recent trades frequency""",
                "category": "trading",
                "difficulty": "intermediate"
            },
            
            "what is risk management": {
                "answer": """⚠️ **Risk Management Essentials**

**Golden rules of trading:**

**1. Position Sizing**
Never risk more than 1-2% of portfolio per trade

**2. Start Small**
- Begin with 0.001 BTC trades
- Learn without big risk

**3. Use Limit Orders**
- Control your entry/exit price
- Avoid slippage

**4. Track Your Portfolio**
- Monitor total value
- Know your exposure

**The 1% Rule:** If you have $10,000, risk max $100 per trade!""",
                "category": "risk",
                "difficulty": "intermediate"
            },
            
            # ==================== ADVANCED CONCEPTS ====================
            "what is arbitrage": {
                "answer": """🔄 **Arbitrage Trading Explained**

**Arbitrage** = Profiting from price differences across markets.

**Simple example:**
- Exchange A price: $50,000
- Exchange B price: $50,100
- Buy on A, sell on B = $100 profit

**Requirements:**
- Fast execution
- Access to multiple venues
- Low fees

**Our future feature:** Smart Order Routing will automatically find best prices!""",
                "category": "advanced",
                "difficulty": "advanced"
            },
            
            "what is market making": {
                "answer": """🏦 **Market Making Strategy**

**Market making** = Providing liquidity by placing both buy and sell orders.

**How it works:**
1. Place bid (buy) at price X
2. Place ask (sell) at price X + spread
3. Profit from spread when both execute

**Example:**
- Buy limit: $49,900
- Sell limit: $50,100  
- Spread profit: $200 per cycle

**In our order book:** Market makers provide depth!""",
                "category": "advanced",
                "difficulty": "advanced"
            },
            
            # ==================== APP TUTORIALS ====================
            "how to place first trade": {
                "answer": """🎯 **Step-by-Step: First Trade**

**1. Choose Side**
- Click **BUY** if you think price will go up
- Click **SELL** if you think price will go down

**2. Pick Order Type**
- **Market Order**: Buy/sell NOW (simpler for beginners)
- **Limit Order**: Buy/sell at specific price (more control)

**3. Enter Quantity**
- Start small (0.001 BTC recommended)
- Check total value preview

**4. Place Order**
- Click "Place Order" button
- Watch it execute instantly!

**5. Monitor**
- Check "Recent Trades" for execution
- Portfolio updates automatically

**Practice tip:** Start with a small market order to see instant results!""",
                "category": "tutorial",
                "difficulty": "beginner"
            },
            
            "how to cancel order": {
                "answer": """❌ **Canceling Open Orders**

**When to cancel:**
- Changed your mind about price
- Market moved against you
- Need funds for another trade

**How to cancel:**
1. Go to "My Open Orders" section
2. Find the order you want to cancel
3. Click the cancel button
4. Order disappears immediately

**Important notes:**
- Can only cancel LIMIT orders
- No fees for canceling
- Funds return to available balance instantly""",
                "category": "tutorial",
                "difficulty": "beginner"
            },
            
            "how to read portfolio": {
                "answer": """💼 **Understanding Your Portfolio**

**Portfolio display shows:**

**1. Cash Balance**
- Your USD available for trading
- Updates after each trade

**2. BTC Balance**  
- Your cryptocurrency holdings
- Increases when you buy, decreases when you sell

**3. Total Value**
- Cash + (BTC × Current Price)
- Your net worth in USD

**4. Current Price**
- Last traded price
- Used to calculate total value

**Example portfolio:**
- Cash: $5,000
- BTC: 0.5 BTC
- Price: $50,000
- Total value: $30,000""",
                "category": "tutorial",
                "difficulty": "beginner"
            },
            
            "trading strategies for beginners": {
                "answer": """🌱 **Beginner Trading Strategies**

**1. Dollar Cost Averaging (DCA)**
- Buy fixed amount regularly (e.g., $100 weekly)
- Removes timing pressure

**2. Trend Following**
- Buy when price above moving average
- Sell when price breaks below

**3. Support/Resistance**
- Buy near support (price floor)
- Sell near resistance (price ceiling)

**4. Paper Trading First**
- Practice with small amounts
- Learn without big risk

**Remember:**
- Start small
- Use stop losses
- Keep a trading journal
- Never revenge trade""",
                "category": "education",
                "difficulty": "beginner"
            }
        }
        
        # Quick responses for common questions
        self.quick_responses = {
            "hello": "👋 Hello! I'm your trading tutor. Ask me anything about trading, the app, or financial concepts!",
            "hi": "👋 Hi there! Ready to learn trading? Try asking: 'How to place first trade' or 'What is a limit order'",
            "hey": "👋 Hey! I'm here to help you learn trading. What would you like to know?",
            "help": """📚 **I can help you with:**

**Basic Concepts:**
- What is a limit/market order?
- How to read order book?
- What is spread?

**Trading Skills:**
- Risk management
- Reading charts
- Trading strategies

**App Tutorials:**
- How to place first trade
- How to cancel orders
- Understanding portfolio

**Advanced Topics:**
- Arbitrage strategies
- Market making
- Liquidity analysis

Just type your question! 💡""",
            "thanks": "You're welcome! 🎓 Keep learning and happy trading!",
            "thank you": "Glad to help! 📈 Remember: knowledge is your best trading tool!"
        }
    
    def get_answer(self, question: str, user_id: str = "default") -> dict:
        """Get answer for user question"""
        question_lower = question.lower().strip()
        
        # Check quick responses
        for key, response in self.quick_responses.items():
            if key in question_lower:
                return {
                    "answer": response,
                    "type": "quick",
                    "suggestions": self.get_suggestions()
                }
        
        # Search knowledge base
        for key, value in self.knowledge_base.items():
            if key in question_lower:
                # Store conversation history
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []
                
                self.conversation_history[user_id].append({
                    "question": question,
                    "answer": value["answer"],
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "answer": value["answer"],
                    "type": "educational",
                    "category": value.get("category", "general"),
                    "suggestions": self.get_suggestions()
                }
        
        # No match found
        return {
            "answer": self.get_fallback_response(),
            "type": "fallback",
            "suggestions": self.get_suggestions()
        }
    
    def calculate_match_score(self, question: str, key: str) -> float:
        """Calculate how well question matches a knowledge base key"""
        question_words = set(question.split())
        key_words = set(key.split())
        
        if not question_words or not key_words:
            return 0
        
        intersection = question_words.intersection(key_words)
        union = question_words.union(key_words)
        
        return len(intersection) / len(union) if union else 0
    
    def get_suggestions(self) -> List[str]:
        """Get suggested questions"""
        return [
            "What is a limit order?",
            "What is a market order?",
            "How to place first trade?",
            "What is risk management?",
            "Help"
        ]
    
    def get_fallback_response(self) -> str:
        """Response when no match found"""
        return """🤔 I'm not sure about that yet. Let me teach you what I know!

**Try asking:**
- "What is a limit order?"
- "How to place first trade?"
- "What is risk management?"
- "How to read order book?"

Or type "help" for all topics I cover! 📚"""
    
    def get_welcome_message(self) -> str:
        """Get welcome message for new users"""
        return """👋 **Welcome to the Trading Engine Tutor!**

I'm your personal AI assistant for learning trading and using this app.

**Here's what I can teach you:**
- 📚 **Trading Basics**: Limit orders, market orders, order books
- 🎯 **App Tutorials**: How to place trades, cancel orders, track portfolio
- ⚠️ **Risk Management**: Position sizing, safe trading practices

**Try asking me:**
- "What is a limit order?"
- "How to place first trade?"
- "What is risk management?"
- "Help"

Let's start your trading journey! 🚀"""


# Create a singleton instance for easy import
chatbot = FinanceTutor()