"""
COMPLETE FIXED CHATBOT - Answers ALL Trading Questions
Covers: Limit/Market Orders, Order Book, Spread, Risk Management, Charts, Strategies, App Navigation
"""

import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class FinanceTutor:
    """Complete educational chatbot for trading and app navigation"""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.user_skill_levels: Dict[str, str] = {}
        
        # ==================== KNOWLEDGE BASE WITH EXACT MATCHES ====================
        self.knowledge_base = {
            
            # ========== LIMIT ORDER ==========
            "limit order": {
                "answer": """📚 **LIMIT ORDER - Complete Guide**

**What is a Limit Order?**
A limit order lets you buy or sell at a specific price or better.

**How it works:**
- 🟢 **BUY LIMIT**: Set the MAXIMUM price you'll pay
  Example: Buy BTC at $45,000 (current price $50,000)
  Your order waits until price drops to $45,000
  
- 🔴 **SELL LIMIT**: Set the MINIMUM price you'll accept
  Example: Sell BTC at $55,000 (current price $50,000)
  Your order waits until price rises to $55,000

**Real Example:**
You want to buy Bitcoin at $45,000. Current price is $50,000. 
Your limit order sits in the order book. When price drops to $45,000, 
it executes automatically at exactly $45,000.

**Pros:** 
✅ Price control - you never pay more than you want
✅ No slippage - execution at your exact price
✅ Can be used for entries AND exits

**Cons:** 
❌ May never execute if price doesn't reach your limit
❌ Requires patience

**When to use Limit Orders:**
- Entering positions at support levels
- Taking profits at resistance levels
- Trading during high volatility
- When you're not in a hurry

**In our app - How to place a Limit Order:**
1. Go to the Trading page (click "Trading" in left sidebar)
2. Click BUY or SELL button
3. Select "Limit Order" from the dropdown menu
4. Enter your desired price
5. Enter quantity (start with 0.001 BTC)
6. Click "Place Order"
7. Your order appears in the Order Book under Bids (buy) or Asks (sell)

**How to see your Limit Order:**
- Look at the Order Book on the Trading page
- Green side (Bids) = your buy limit orders
- Red side (Asks) = your sell limit orders
- Also check "My Open Orders" section

**How to Cancel a Limit Order:**
- Go to "My Open Orders" section
- Click the red X next to your order
- Order cancels instantly, funds return to balance

**Pro Tip:** Use limit orders to "catch falling knives" and buy dips!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            # ========== MARKET ORDER ==========
            "market order": {
                "answer": """📚 **MARKET ORDER - Complete Guide**

**What is a Market Order?**
A market order buys or sells IMMEDIATELY at the best available price.

**How it works:**
- Instant execution (milliseconds)
- Matches with existing orders in the book
- Guaranteed to fill, but price may vary

**Real Example:**
Bitcoin is trading at $50,000 (bid) / $50,100 (ask)
- You place a MARKET BUY order → fills at $50,100
- You place a MARKET SELL order → fills at $50,000

**Pros:** 
✅ Guaranteed execution - your order WILL fill
✅ Fastest possible speed
✅ Simple to use - no price entry needed

**Cons:** 
❌ Price uncertainty - may get worse price
❌ Slippage possible in volatile markets
❌ You always pay the spread

**When to use Market Orders:**
- Entering/exiting positions quickly
- Trading highly liquid assets (BTC, ETH)
- When speed matters more than price
- For small order sizes

**In our app - How to place a Market Order:**
1. Go to the Trading page (click "Trading" in left sidebar)
2. Click BUY or SELL button
3. Select "Market Order" from the dropdown menu
4. Enter quantity only (no price needed!)
5. Click "Place Order"
6. Your order executes IMMEDIATELY

**What happens after placing:**
- Order fills instantly
- Check "Recent Trades" to see execution
- Your portfolio updates automatically
- The order book updates in real-time

**Slippage Warning:**
If you try to buy 10 BTC with a market order and there's only 5 BTC at $50,000, 
the next 5 BTC might cost $50,100 or more!

**Pro Tip:** For first-time traders, market orders are simpler. Start with tiny sizes (0.001 BTC) to learn!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            # ========== ORDER BOOK ==========
            "order book": {
                "answer": """📚 **ORDER BOOK - Complete Guide**

**What is the Order Book?**
The order book shows ALL pending buy and sell orders in real-time.

**Two Main Sides:**

**🟢 BIDS (Buy Orders) - LEFT SIDE**
- People wanting to BUY
- Sorted by HIGHEST price first
- Shown in GREEN
- Example: $49,900 for 0.5 BTC

**🔴 ASKS (Sell Orders) - RIGHT SIDE**
- People wanting to SELL
- Sorted by LOWEST price first
- Shown in RED
- Example: $50,100 for 1 BTC

**Key Terms:**
- **Best Bid**: Highest price someone will buy at (top of green side)
- **Best Ask**: Lowest price someone will sell at (top of red side)
- **Spread**: Difference between Best Ask and Best Bid
- **Depth**: How many orders at each price level

**How to Read Our App's Order Book:**

On the Trading page, you'll see:

**LEFT COLUMN (Bids - Green):**
Price Size Total
$49,900 0.5 $24,950 ← Best Bid
$49,800 1.0 $49,800
$49,700 1.5 $74,550

**MIDDLE SECTION:**
Spread: $200 (0.4%)

**RIGHT COLUMN (Asks - Red):**
Price Size Total
$50,100 1.0 $50,100 ← Best Ask
$50,200 0.8 $40,160
$50,300 0.5 $25,150

**How Trades Happen:**
- Highest Bid ($49,900) matches with Lowest Ask ($50,100)
- When they meet, a trade executes
- This is called "price-time priority"

**What Order Book Tells You:**

1. **Support Levels**: Large green clusters = price likely to bounce up
2. **Resistance Levels**: Large red clusters = price likely to stall
3. **Market Sentiment**: More green = bullish, more red = bearish
4. **Liquidity**: Deep book = easy to trade large sizes

**In our app - How to use the Order Book:**

1. **To place a Limit Order:**
   - Click on any price in the order book
   - It auto-fills the price field
   - Enter quantity and place order

2. **To see Market Depth:**
   - Scroll through bids and asks
   - Look for large clusters (walls)
   - These act as support/resistance

3. **To check Spread:**
   - Look at the middle section
   - Spread displayed in $ and %
   - Tight spread = good liquidity

**Pro Tip:** Watch how the order book changes during volatile times. Large orders appearing/disappearing can signal price moves!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            # ========== SPREAD ==========
            "spread": {
                "answer": """📚 **BID-ASK SPREAD - Complete Guide**

**What is Spread?**
The spread is the DIFFERENCE between the highest buy order (bid) and lowest sell order (ask).

**Formula:** 
Spread = Best Ask - Best Bid
Spread % = (Spread ÷ Best Ask) × 100

**Example:**
- Best Bid (someone wants to buy): $49,900
- Best Ask (someone wants to sell): $50,100
- Spread = $50,100 - $49,900 = $200
- Spread % = ($200 ÷ $50,100) × 100 = 0.4%

**What Spreads Tell You:**

| Spread Size | Meaning | Action |
|-------------|---------|--------|
| <0.1% | Very Liquid | Market orders safe |
| 0.1-0.5% | Normal | Limit orders recommended |
| 0.5-1% | Low Liquidity | Use limit orders only |
| >1% | Very Low | Avoid trading |

**How Spread Affects Your Trades:**

**With Market Orders:**
- You IMMEDIATELY lose the spread
- Buy at ask ($50,100), sell at bid ($49,900)
- Price must move $200 just to break even!

**With Limit Orders:**
- You can CAPTURE the spread
- Place bid at $49,900, ask at $50,100
- Profit $200 when both execute

**In our app - Where to find Spread:**
1. Go to Trading page
2. Look BETWEEN the bids and asks
3. Spread displayed as: "Spread: $200 (0.4%)"

**How to Trade with Spread:**

**Strategy 1 - Avoid Paying Spread:**
- Use limit orders instead of market orders
- Be patient for fills
- Save on transaction costs

**Strategy 2 - Capture Spread (Market Making):**
- Place bid at best bid price
- Place ask at best ask price
- Profit when both fill
- Requires monitoring

**When Spread Widens:**
- During news events
- Low liquidity hours (weekends)
- High volatility
- Market manipulation

**Pro Tip:** Check spread before placing any market order. If spread >0.5%, use limit orders instead!""",
                "category": "basics",
                "difficulty": "beginner"
            },
            
            # ========== RISK MANAGEMENT ==========
            "risk management": {
                "answer": """⚠️ **RISK MANAGEMENT - Complete Guide**

**What is Risk Management?**
Risk management is protecting your trading capital from large losses.

**The Golden Rules:**

**1. Position Sizing (The 1% Rule)**
Never risk more than 1-2% of your portfolio on any single trade.

**Formula:**
Position Size = (Account × Risk%) ÷ Stop Loss %
Example: $10,000 account × 1% = $100 risk per trade

**2. Stop Losses**
- ALWAYS set a stop loss before entering a trade
- Predetermined exit if trade goes wrong
- Removes emotion from trading
- Place 1-2% below support (for buys)

**3. Take Profits**
- Set profit targets before entering
- Lock in gains at resistance levels
- Scale out partially (take some profit, let rest run)

**4. Risk-Reward Ratio**
- Minimum 1:2 (risk $1 to make $2)
- Better is 1:3 or higher
- You can be wrong 50% of time and still profit!

**Risk-Reward Table:**
| Risk | Reward | Ratio | Win Rate Needed |
|------|--------|-------|-----------------|
| $100 | $200 | 1:2 | 33% |
| $100 | $300 | 1:3 | 25% |
| $100 | $500 | 1:5 | 17% |

**5. Diversification**
- Don't put all capital in one trade
- Trade different assets
- Keep some cash for opportunities

**The 1% Rule in Action:**
Account Size: $10,000
Max Risk per Trade: $100 (1%)
Stop Loss: 2% ($1,000 per BTC)
Position Size = $100 ÷ $1,000 = 0.1 BTC

**In our app - Risk Management Features:**

1. **Balance Checks:**
   - App checks your balance before orders
   - Won't let you spend more than you have
   - Shows error message if insufficient funds

2. **Order Size Limits:**
   - Maximum 10 BTC per order
   - Prevents over-trading
   - Protects new traders

3. **Portfolio Tracking:**
   - Real-time balance updates
   - Shows total value
   - Track your profit/loss

**How to Practice Risk Management in Our App:**

**Step 1: Start Small**
- Begin with 0.001 BTC trades (about $50)
- This is 0.5% of a $10,000 account
- Very low risk to learn

**Step 2: Use Stop Losses**
- Place limit orders below support
- If price drops, you exit automatically
- Never hold losing trades

**Step 3: Track Your Portfolio**
- Check portfolio page regularly
- Monitor total value
- Don't let drawdown exceed 20%

**Step 4: Keep a Trading Journal**
- Log every trade
- Note entry, exit, risk, reward
- Review weekly to improve

**Common Risk Mistakes:**
- ❌ Risking too much per trade (>2%)
- ❌ Moving stop losses further away
- ❌ Adding to losing positions
- ❌ Trading without a stop loss
- ❌ Overtrading (too many positions)

**Pro Tip:** The #1 rule of trading is "protect your capital." You can't trade if you have no money left!""",
                "category": "risk",
                "difficulty": "intermediate"
            },
            
            # ========== READING CHARTS ==========
            "reading charts": {
                "answer": """📊 **READING CHARTS - Complete Guide**

**What are Trading Charts?**
Charts show price movements over time. They help you predict where price might go next.

**Types of Charts in Our App:**

**1. Line Chart**
- Connects closing prices
- Simple and clean
- Best for: Trend identification

**2. Candlestick Chart (MOST POPULAR)**
- Shows Open, High, Low, Close
- Each candle = one time period
- GREEN candle = price went UP
- RED candle = price went DOWN

**Candlestick Anatomy:**
HIGH ─┬─ (Upper Wick - price peaked here)
│
CLOSE ─┼─ (For green candles - closing price)
or │
OPEN ─┼─ (For red candles - opening price)
│
BODY │ (Shows open to close range)
│
OPEN ─┼─ (For green candles - opening price)
or │
CLOSE ─┼─ (For red candles - closing price)
│
LOW ─┴─ (Lower Wick - price bottomed here)

**What Candles Tell You:**

**Long Green Candle:**
- Strong buying pressure
- Bullish sentiment
- Price likely to continue up

**Long Red Candle:**
- Strong selling pressure
- Bearish sentiment
- Price likely to continue down

**Small Body (Doji):**
- Indecision in market
- Buyers and sellers equal
- Potential reversal coming

**Long Wicks (Rejection):**
- Price tried to go further but got rejected
- Upper wick = sellers pushed price down
- Lower wick = buyers pushed price up

**In our app - How to Read the Chart:**

1. **Go to Trading page**
2. **Look at the price chart** (top section)
3. **Each candle = 1 minute** of trading
4. **Green candles** = price increased that minute
5. **Red candles** = price decreased that minute

**Support and Resistance on Charts:**

**SUPPORT (Floor):**
- Price level where buying pressure EXCEEDS selling
- Price tends to BOUNCE UP from support
- Draw horizontal line at recent lows
- More touches = stronger support

**RESISTANCE (Ceiling):**
- Price level where selling pressure EXCEEDS buying
- Price tends to BOUNCE DOWN from resistance
- Draw horizontal line at recent highs
- More touches = stronger resistance

**How to Identify Support/Resistance:**

1. **Look for price reversal points**
2. **Draw lines at those levels**
3. **Watch how price reacts**
4. **Strong levels = 3+ touches**

**Chart Patterns to Watch:**

**Bullish Patterns (Price likely UP):**
- **Higher Lows**: Uptrend forming
- **Breakout above resistance**: Price breaks ceiling
- **Double Bottom**: Price bounces twice at same level

**Bearish Patterns (Price likely DOWN):**
- **Lower Highs**: Downtrend forming
- **Breakdown below support**: Price breaks floor
- **Double Top**: Price rejects twice at same level

**In our app - Chart Features:**

1. **Real-time updates** - Chart moves with every trade
2. **Zoom in/out** - See different timeframes
3. **Price on hover** - See exact price at any point

**How to Use Charts for Trading:**

**Step 1: Identify Trend**
- Are highs getting higher? = Uptrend (look to BUY)
- Are lows getting lower? = Downtrend (look to SELL)

**Step 2: Find Support/Resistance**
- Draw lines at recent highs/lows
- These are your entry/exit zones

**Step 3: Wait for Price to Reach Levels**
- At support → Consider BUYING
- At resistance → Consider SELLING

**Step 4: Use Candles for Confirmation**
- Green candle at support = bullish signal
- Red candle at resistance = bearish signal

**Pro Tip:** Start with the 1-minute chart for day trading, 1-hour for swing trading. Higher timeframes show stronger trends!""",
                "category": "analysis",
                "difficulty": "intermediate"
            },
            
            # ========== TRADING STRATEGIES ==========
            "trading strategies": {
                "answer": """🎯 **TRADING STRATEGIES - Complete Guide**

**What are Trading Strategies?**
A trading strategy is a set of rules that tells you WHEN to buy, WHEN to sell, and HOW MUCH to risk.

**Strategy 1: Scalping (For Beginners)**
- **What**: Many small profits from tiny price moves
- **Timeframe**: Seconds to minutes
- **Target**: 0.1-0.5% profit per trade
- **Trades per day**: 10-50
- **Best for**: Active traders who watch charts all day

**How to scalp in our app:**
1. Watch 1-minute chart
2. Look for small price movements
3. Use MARKET orders for speed
4. Take profit quickly (don't be greedy)
5. Cut losses FAST (0.2% max)

**Strategy 2: Day Trading**
- **What**: Open and close positions within same day
- **Timeframe**: Minutes to hours
- **Target**: 1-2% profit per trade
- **Trades per day**: 5-20
- **Best for**: Full-time traders

**How to day trade in our app:**
1. Check chart at market open
2. Identify trend for the day
3. Trade in trend direction
4. Close ALL positions before day ends
5. No overnight holding

**Strategy 3: Swing Trading (Best for Beginners)**
- **What**: Capture moves over days to weeks
- **Timeframe**: Daily and 4-hour charts
- **Target**: 5-10% profit per trade
- **Trades per week**: 2-5
- **Best for**: Part-time traders

**How to swing trade in our app:**
1. Look at daily chart for trend
2. Find support/resistance levels
3. Enter at support (for buys)
4. Set stop loss 2-3% below entry
5. Target next resistance level

**Strategy 4: Trend Following**
- **What**: Buy in uptrends, sell in downtrends
- **Timeframe**: Any
- **The trend is your friend!

**How to trend follow in our app:**
1. Identify trend direction
2. Higher highs = Uptrend (BUY)
3. Lower lows = Downtrend (SELL)
4. Enter on pullbacks
5. Exit when trend reverses

**Strategy 5: Breakout Trading**
- **What**: Trade when price breaks support/resistance
- **Timeframe**: Any
- **High reward potential**

**How to trade breakouts in our app:**
1. Identify key support/resistance levels
2. Wait for price to break through
3. Enter on the breakout candle
4. Stop loss just below breakout
5. Target = height of previous range

**Which Strategy is Best for YOU?**

| Experience | Recommended Strategy | Time Commitment |
|------------|---------------------|-----------------|
| Complete Beginner | Paper trade first | As much as you want |
| Week 1-2 | Tiny market orders | 30 min/day |
| Week 3-4 | Limit orders | 1 hour/day |
| Month 2 | Swing trading | 2 hours/day |
| Month 3+ | Day trading | Full-time |

**In our app - How to Practice Strategies:**

**Step 1: Start with Paper Trading**
- Use tiny amounts (0.001 BTC)
- Treat it like real money
- No risk to learn

**Step 2: Master One Strategy**
- Don't jump between strategies
- Pick one and stick with it
- Practice until profitable

**Step 3: Keep a Trading Journal**
- Log every trade
- Entry reason, exit reason, profit/loss
- Review weekly to improve

**Step 4: Scale Up Gradually**
- Start with 0.001 BTC
- After 20 profitable trades, increase to 0.01 BTC
- After 50 profitable trades, increase to 0.1 BTC

**Strategy Rules for ALL Traders:**

1. **Always use a stop loss**
2. **Never risk more than 1-2% per trade**
3. **Keep risk-reward at least 1:2**
4. **Don't trade during news events**
5. **Take breaks to avoid burnout**

**Pro Tip:** The best strategy is the one you can stick with consistently. Start simple and master it before moving to advanced strategies!""",
                "category": "strategies",
                "difficulty": "intermediate"
            },
            
            # ========== APP NAVIGATION ==========
            "how to navigate the app": {
                "answer": """🗺️ **APP NAVIGATION - Complete Guide**

**Welcome to the Trading Engine! Here's how to navigate everything.**

**LOGIN PAGE:**

When you first open the app, you'll see the Login page:
- **Username field**: Enter your username
- **Password field**: Enter your password
- **Login button**: Click to enter
- **Register button**: Create new account
- **Demo buttons**: Try with admin/demo accounts

**AFTER LOGIN - MAIN DASHBOARD:**

You'll see a dark-themed trading interface with:

**LEFT SIDEBAR (Navigation Menu):**
- 🏠 **Dashboard** - Main overview
- 📊 **Trading** - Place orders and see charts
- 💼 **Portfolio** - Check your balances
- 📜 **Orders** - View order history
- ⭐ **Watchlist** - Track favorite symbols
- 🚪 **Logout** - Exit the app

**TOP BAR:**
- Shows current page name
- Your username with avatar
- Connection status (green dot = connected)

**TRADING PAGE (Most Important):**

This is where you place trades. The page has several sections:

**1. Market Status Card (Top)**
- Current BTC price
- 24-hour change percentage
- Connection status

**2. Price Chart (Middle-Left)**
- Shows candlestick chart
- Updates in real-time
- Hover to see prices

**3. Order Form (Middle-Right)**
- BUY/SELL toggle buttons
- Order type dropdown (Market/Limit)
- Price field (for limit orders)
- Quantity field
- Total value preview
- PLACE ORDER button

**4. Order Book (Bottom-Left)**
- Left side: Bids (green) - people buying
- Right side: Asks (red) - people selling
- Middle: Spread display
- Click any price to auto-fill order form

**5. Recent Trades (Bottom-Right)**
- Shows latest executed trades
- Time, price, and quantity
- Updates in real-time

**PORTFOLIO PAGE:**

Shows your financial status:
- **Cash Balance**: USD available
- **Crypto Balance**: BTC holdings
- **Total Value**: Cash + BTC value
- **Trade History**: All your past trades

**ORDERS PAGE:**

Shows all your orders:
- **Open Orders**: Limit orders waiting to fill
- **Order History**: Past orders
- **Status**: Filled, Cancelled, Open, Rejected
- **Cancel button**: Red X to cancel open orders

**WATCHLIST PAGE:**

Track your favorite symbols:
- **Add Symbol**: Button to add new symbols
- **Alert Price**: Set price notifications
- **Remove**: Delete from watchlist

**CHATBOT (Bottom-Right Corner):**
- Green chat bubble icon
- Click to open trading tutor
- Ask any trading question
- Get instant educational answers

**HOW TO PLACE YOUR FIRST TRADE:**

**Step-by-Step:**
1. Click "Trading" in left sidebar
2. Click GREEN "BUY" button (or RED "SELL")
3. Select "Market Order" (simpler for first trade)
4. Enter quantity: type "0.001" (very small!)
5. Click "Place Order"
6. Watch it execute instantly
7. Check "Recent Trades" to see your trade
8. Go to "Portfolio" to see updated balance

**HOW TO PLACE A LIMIT ORDER:**
1. Click "Trading"
2. Choose BUY or SELL
3. Select "Limit Order" from dropdown
4. Enter price (e.g., 45000)
5. Enter quantity (e.g., 0.01)
6. Click "Place Order"
7. Order appears in Order Book
8. Check "My Open Orders" to see it pending

**HOW TO CANCEL AN ORDER:**
1. Go to "Orders" page
2. Find your open order
3. Click the red X (Cancel button)
4. Order disappears immediately
5. Funds return to your balance

**HOW TO CHECK YOUR PROFIT/LOSS:**
1. Go to "Portfolio" page
2. See your Total Value
3. Compare to initial $10,000
4. Difference = your profit/loss

**HOW TO USE THE CHATBOT:**
1. Look for green chat bubble (bottom-right)
2. Click to open
3. Type your question
4. Get instant answer
5. Try: "What is a limit order?" or "How to place first trade?"

**TIPS FOR NEW USERS:**

1. **Start with tiny trades** (0.001 BTC = about $50)
2. **Use Market Orders first** (simpler)
3. **Watch the order book** to learn how price moves
4. **Ask the chatbot** whenever confused
5. **Check portfolio after each trade** to see impact
6. **Practice for a week** before trading larger sizes

**Keyboard Shortcuts (Coming Soon):**
- **B** = Buy
- **S** = Sell
- **M** = Market order
- **L** = Limit order
- **Enter** = Place order

**Need Help?**
- Click the chatbot (green bubble)
- Type your question
- I'll guide you through anything!

**Pro Tip:** Bookmark this guide! You'll refer to it often as you learn the platform.""",
                "category": "tutorial",
                "difficulty": "beginner"
            },
            
            # ========== ARBITRAGE ==========
            "arbitrage": {
                "answer": """🔄 **ARBITRAGE STRATEGY - Complete Guide**

**What is Arbitrage?**
Arbitrage is profiting from price differences of the same asset across different markets.

**Simple Example:**
Exchange A: BTC = $50,000
Exchange B: BTC = $50,100
Buy on A ($50,000), Sell on B ($50,100)
Profit = $100 per BTC (minus fees)

**Types of Arbitrage:**

**1. Spatial Arbitrage**
- Same asset, different exchanges
- Requires accounts on multiple exchanges
- Fast execution needed (seconds matter)
- Profit from price inefficiencies

**2. Triangular Arbitrage**
- Three currencies on same exchange
- Example: BTC → ETH → USDT → BTC
- Profits from price discrepancies

**3. Statistical Arbitrage**
- Correlated assets that diverge
- Mean reversion strategy
- Requires complex algorithms

**Requirements for Arbitrage:**

1. **Fast Execution**
   - Milliseconds matter
   - Automated trading recommended
   - Manual arbitrage is too slow

2. **Low Fees**
   - Maker/taker fees must be very low
   - Withdrawal/deposit fees factor in
   - Profit margins are tiny (0.1-0.5%)

3. **Significant Capital**
   - Profits per trade are small
   - Need size for meaningful returns
   - Example: 0.1% profit on $10,000 = $10

4. **Multiple Exchange Accounts**
   - Funds on both exchanges
   - Ready to execute both legs
   - Withdrawal time matters

**Arbitrage Formula:**
Profit = (Price B - Price A) - (Fees + Slippage)
If Profit > 0, opportunity exists

**Risks of Arbitrage:**

1. **Execution Risk**: One leg fills, other doesn't
2. **Timing Risk**: Price changes during execution
3. **Withdrawal Risk**: Funds stuck during transfer
4. **Fee Risk**: Fees eat all profits
5. **Competition**: Many bots doing same thing

**In our app:** We're adding Smart Order Routing to automatically find best prices across markets!

**For Beginners:** Arbitrage is advanced. Start with simple strategies first!""",
                "category": "advanced",
                "difficulty": "advanced"
            },
            
            # ========== MARKET MAKING ==========
            "market making": {
                "answer": """🏦 **MARKET MAKING STRATEGY - Complete Guide**

**What is Market Making?**
Market making is providing liquidity by placing both buy and sell orders.

**How Market Making Works:**

1. **Place Bid Order (Buy)**
   - Below current market price
   - Example: Buy BTC at $49,900

2. **Place Ask Order (Sell)**
   - Above current market price
   - Example: Sell BTC at $50,100

3. **Profit from Spread**
   - Capture the difference when both execute
   - Example profit: $200 per cycle

**Market Making Example:**
Current Price: $50,000

You place:

Buy order: 1 BTC @ $49,900

Sell order: 1 BTC @ $50,100

If both execute:

Buy at $49,900

Sell at $50,100

Profit: $200 (minus fees)

**Requirements for Market Making:**

1. **Fast Technology**
   - Low latency connections
   - Automated trading systems
   - Need to adjust quotes quickly

2. **Inventory Management**
   - Manage risk of holding inventory
   - Hedge when needed
   - Rebalance positions

3. **Capital Requirements**
   - Need funds for both sides
   - Usually significant capital
   - Example: $100,000+

4. **Risk Controls**
   - Stop losses
   - Position limits
   - Volatility adjustments

**In our app:** Watch how market makers provide order book depth! The large bid/ask clusters are often market makers.

**For Beginners:** Market making is very advanced. Start with simple trading first!""",
                "category": "advanced",
                "difficulty": "advanced"
            },
            
            # ========== LIQUIDITY ANALYSIS ==========
            "liquidity analysis": {
                "answer": """💧 **LIQUIDITY ANALYSIS - Complete Guide**

**What is Liquidity Analysis?**
Analyzing how easily you can buy or sell an asset without affecting price.

**How to Analyze Liquidity in Our App:**

**1. Check Order Book Depth**
- Look at bids and asks
- Deep book = many orders = good liquidity
- Shallow book = few orders = poor liquidity

**2. Measure the Spread**
- Tight spread (<0.1%) = good liquidity
- Wide spread (>1%) = poor liquidity
- Our app shows spread in real-time

**3. Recent Trade Frequency**
- Many trades per minute = good liquidity
- Few trades per hour = poor liquidity
- Check the trades list

**4. Order Book Imbalance**
- Balanced bids/asks = healthy
- Extreme imbalance = potential issues

**Liquidity Indicators:**

| Indicator | Good Liquidity | Poor Liquidity |
|-----------|----------------|----------------|
| Spread | <0.1% | >1% |
| Order Book Depth | 10+ levels | 2-3 levels |
| Trade Frequency | 10+/minute | 1-2/minute |
| Order Size | 10+ BTC | 0.1 BTC |

**In our app - How to Analyze:**
1. Go to Trading page
2. Look at order book
3. Check spread percentage
4. See how many trades per minute
5. Make trading decisions based on liquidity

**Trading Based on Liquidity:**

**High Liquidity (BTC, ETH):**
- ✅ Market orders safe
- ✅ Large sizes possible
- ✅ Tight stops work

**Low Liquidity (Small Altcoins):**
- ❌ Use limit orders only
- ❌ Small sizes only
- ❌ Wider stops needed

**Pro Tip:** Always check liquidity before placing large orders. BTC/USD has the best liquidity in our app!""",
                "category": "advanced",
                "difficulty": "advanced"
            },
            
            # ========== HELP ==========
            "help": {
                "answer": """📚 **COMPLETE HELP GUIDE**

**I can help you with these topics:**

**🎓 BASIC CONCEPTS:**
- "What is a limit order?" - Buy/sell at specific price
- "What is a market order?" - Buy/sell immediately
- "How to read order book?" - Understanding bids/asks
- "What is spread?" - Difference between bid and ask

**📊 TECHNICAL ANALYSIS:**
- "How to read charts?" - Candlestick guide
- "Support and resistance" - Key price levels
- "Chart patterns" - Head and shoulders, triangles

**⚠️ RISK MANAGEMENT:**
- "What is risk management?" - Protecting capital
- "Position sizing" - How much to trade (1% rule)
- "Stop losses" - Automatic exits

**🎯 TRADING STRATEGIES:**
- "Scalping" - Quick small profits
- "Swing trading" - Days to weeks
- "Day trading" - Same day only
- "Dollar cost averaging" - Regular investing

**🛠️ APP TUTORIALS:**
- "How to navigate the app?" - Complete guide
- "How to place first trade?" - Step by step
- "How to cancel orders?" - Remove open orders
- "How to read portfolio?" - Track your money

**🚀 ADVANCED TOPICS:**
- "Arbitrage strategies" - Price differences
- "Market making" - Providing liquidity
- "Liquidity analysis" - Checking market depth

**💡 QUICK COMMANDS:**
- Type any question naturally
- Example: "How do I buy Bitcoin?"
- Example: "What's a stop loss?"
- Example: "Help me understand charts"

**📱 HOW TO USE THIS CHATBOT:**
1. Click the green chat bubble (bottom-right)
2. Type your question
3. Press Enter or click Send
4. Get instant answer
5. Try suggested questions

**Need specific help? Just ask!** 💬""",
                "category": "help",
                "difficulty": "beginner"
            }
        }
        
        # Quick responses
        self.quick_responses = {
            "hello": "👋 Hello! I'm your trading tutor. Ask me about limit orders, market orders, reading charts, risk management, or how to navigate the app!",
            "hi": "👋 Hi there! Try asking: 'How to place first trade?' or 'What is a limit order?' or 'How to navigate the app?'",
            "hey": "👋 Hey! Ask me anything about trading or using the app!",
            "thanks": "You're welcome! 🎓 Keep learning!",
            "thank you": "Glad to help! 📈",
            "how to navigate": "🗺️ Click 'Trading' in left sidebar to place orders. 'Portfolio' to see balances. 'Orders' to view history. Chatbot is bottom-right green bubble!",
            "how to trade": "🎯 Go to Trading page, click BUY/SELL, choose order type, enter quantity, click Place Order! Start with 0.001 BTC.",
            "how to cancel": "❌ Go to Orders page, find your open order, click the red X button.",
            "how to see balance": "💼 Click 'Portfolio' in left sidebar to see your cash, crypto, and total value."
        }
    
    def get_answer(self, question: str, user_id: str = "default") -> dict:
        """Get answer for user question"""
        question_lower = question.lower().strip()
        
        # Check quick responses first
        for key, response in self.quick_responses.items():
            if key in question_lower:
                return {
                    "answer": response,
                    "type": "quick",
                    "suggestions": self.get_suggestions()
                }
        
        # Search knowledge base
        best_match = None
        best_score = 0
        
        for key, value in self.knowledge_base.items():
            if key in question_lower:
                best_match = value
                best_score = 1
                break
            
            # Check partial matches
            keywords = key.split()
            match_count = sum(1 for kw in keywords if kw in question_lower)
            if match_count > 0:
                score = match_count / len(keywords)
                if score > best_score:
                    best_score = score
                    best_match = value
        
        if best_match and best_score > 0.3:
            # Store history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append({
                "question": question,
                "answer": best_match["answer"][:200],
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "answer": best_match["answer"],
                "type": "educational",
                "category": best_match.get("category", "general"),
                "suggestions": self.get_suggestions()
            }
        
        return {
            "answer": self.get_fallback_response(),
            "type": "fallback",
            "suggestions": self.get_suggestions()
        }
    
    def get_suggestions(self) -> List[str]:
        """Get suggested questions"""
        return [
            "What is a limit order?",
            "What is a market order?",
            "How to read order book?",
            "What is spread?",
            "Risk management",
            "How to read charts?",
            "Trading strategies",
            "How to place first trade?",
            "How to cancel orders?",
            "How to navigate the app?",
            "Arbitrage strategies",
            "Market making",
            "Liquidity analysis",
            "Help"
        ]
    
    def get_fallback_response(self) -> str:
        """Response when no match found"""
        return """📚 **I can help you with:**

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
- How to navigate the app

**Advanced Topics:**
- Arbitrage strategies
- Market making
- Liquidity analysis

**Try asking any of these questions!** Just type what you want to learn about.

For app help, try: "How to navigate the app?" or "How to place first trade?" 💬"""


# Create singleton instance
chatbot = FinanceTutor()