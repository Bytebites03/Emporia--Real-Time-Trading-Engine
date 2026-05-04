import heapq
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    price: float
    quantity: float
    filled_quantity: float = 0
    status: OrderStatus = OrderStatus.PENDING
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    user_id: str = "default_user"
    
    @property
    def remaining_quantity(self) -> float:
        return self.quantity - self.filled_quantity
    
    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "type": self.type.value,
            "price": self.price,
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "user_id": self.user_id
        }

@dataclass
class Trade:
    id: str
    symbol: str
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: float
    timestamp: int
    buyer_id: str
    seller_id: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "buy_order_id": self.buy_order_id,
            "sell_order_id": self.sell_order_id,
            "timestamp": self.timestamp
        }

class MatchingEngine:
    def __init__(self, symbol: str = "BTC/USD"):
        self.symbol = symbol
        # Max heap for bids (buy orders) - store as (-price, timestamp, order)
        self.bids: List[tuple] = []
        # Min heap for asks (sell orders) - store as (price, timestamp, order)
        self.asks: List[tuple] = []
        # Fast lookup for order cancellation
        self.orders: Dict[str, Order] = {}
        # Trade history
        self.trades: List[Trade] = []
        
    def place_order(self, order: Order) -> List[Trade]:
        """Place an order and match immediately"""
        order.status = OrderStatus.OPEN
        order.timestamp = int(datetime.now().timestamp() * 1000)
        self.orders[order.id] = order
        
        trades = []
        
        if order.side == OrderSide.BUY:
            trades = self.match_buy_order(order)
        else:
            trades = self.match_sell_order(order)
            
        # If order not fully filled, add to order book
        if order.remaining_quantity > 0:
            if order.side == OrderSide.BUY:
                heapq.heappush(self.bids, (-order.price, order.timestamp, order))
            else:
                heapq.heappush(self.asks, (order.price, order.timestamp, order))
        else:
            order.status = OrderStatus.FILLED
            
        return trades
    
    def match_buy_order(self, buy_order: Order) -> List[Trade]:
        trades = []
        
        while buy_order.remaining_quantity > 0 and self.asks:
            price, timestamp, sell_order = self.asks[0]
            
            # For limit orders, check price condition
            if buy_order.type == OrderType.LIMIT and buy_order.price < price:
                break
                
            # Pop the best ask
            heapq.heappop(self.asks)
            
            # Execute trade
            trade_quantity = min(buy_order.remaining_quantity, sell_order.remaining_quantity)
            trade_price = price if buy_order.type == OrderType.MARKET else buy_order.price
            
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=self.symbol,
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                price=trade_price,
                quantity=trade_quantity,
                timestamp=int(datetime.now().timestamp() * 1000),
                buyer_id=buy_order.user_id,
                seller_id=sell_order.user_id
            )
            trades.append(trade)
            self.trades.append(trade)
            
            # Update order quantities
            buy_order.filled_quantity += trade_quantity
            sell_order.filled_quantity += trade_quantity
            
            # Re-push sell order if not fully filled
            if sell_order.remaining_quantity > 0:
                heapq.heappush(self.asks, (sell_order.price, sell_order.timestamp, sell_order))
            else:
                sell_order.status = OrderStatus.FILLED
                
        if buy_order.filled_quantity > 0:
            buy_order.status = OrderStatus.PARTIAL if buy_order.remaining_quantity > 0 else OrderStatus.FILLED
            
        return trades
    
    def match_sell_order(self, sell_order: Order) -> List[Trade]:
        trades = []
        
        while sell_order.remaining_quantity > 0 and self.bids:
            neg_price, timestamp, buy_order = self.bids[0]
            price = -neg_price
            
            # For limit orders, check price condition
            if sell_order.type == OrderType.LIMIT and sell_order.price > price:
                break
                
            # Pop the best bid
            heapq.heappop(self.bids)
            
            # Execute trade
            trade_quantity = min(sell_order.remaining_quantity, buy_order.remaining_quantity)
            trade_price = price if sell_order.type == OrderType.MARKET else sell_order.price
            
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=self.symbol,
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                price=trade_price,
                quantity=trade_quantity,
                timestamp=int(datetime.now().timestamp() * 1000),
                buyer_id=buy_order.user_id,
                seller_id=sell_order.user_id
            )
            trades.append(trade)
            self.trades.append(trade)
            
            # Update order quantities
            sell_order.filled_quantity += trade_quantity
            buy_order.filled_quantity += trade_quantity
            
            # Re-push buy order if not fully filled
            if buy_order.remaining_quantity > 0:
                heapq.heappush(self.bids, (-buy_order.price, buy_order.timestamp, buy_order))
            else:
                buy_order.status = OrderStatus.FILLED
                
        if sell_order.filled_quantity > 0:
            sell_order.status = OrderStatus.PARTIAL if sell_order.remaining_quantity > 0 else OrderStatus.FILLED
            
        return trades
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in [OrderStatus.OPEN, OrderStatus.PARTIAL]:
                order.status = OrderStatus.CANCELLED
                return True
        return False
    
    def get_order_book(self, depth: int = 10) -> dict:
        """Get current order book snapshot"""
        bids = []
        for neg_price, ts, order in self.bids[:depth]:
            if order.status == OrderStatus.OPEN:
                bids.append([-neg_price, order.remaining_quantity])
                
        asks = []
        for price, ts, order in self.asks[:depth]:
            if order.status == OrderStatus.OPEN:
                asks.append([price, order.remaining_quantity])
                
        return {
            "symbol": self.symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
    
    def get_recent_trades(self, limit: int = 50) -> List[dict]:
        return [trade.to_dict() for trade in self.trades[-limit:]]
    
# Add to MatchingEngine class in matching_engine.py

def get_order_book_depth(self, levels: int = 10) -> dict:
    """Get order book with cumulative depth"""
    bids_depth = []
    cumulative_bid = 0
    
    for neg_price, ts, order in self.bids[:levels]:
        if order.status == OrderStatus.OPEN:
            cumulative_bid += order.remaining_quantity
            bids_depth.append({
                'price': -neg_price,
                'size': order.remaining_quantity,
                'cumulative': cumulative_bid,
                'value': (-neg_price) * cumulative_bid
            })
    
    asks_depth = []
    cumulative_ask = 0
    
    for price, ts, order in self.asks[:levels]:
        if order.status == OrderStatus.OPEN:
            cumulative_ask += order.remaining_quantity
            asks_depth.append({
                'price': price,
                'size': order.remaining_quantity,
                'cumulative': cumulative_ask,
                'value': price * cumulative_ask
            })
    
    return {
        'bids': bids_depth,
        'asks': asks_depth,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }

def get_market_depth_chart(self, levels: int = 20) -> dict:
    """Get data for market depth chart"""
    bids = []
    for neg_price, ts, order in self.bids[:levels]:
        if order.status == OrderStatus.OPEN:
            bids.append({'price': -neg_price, 'size': order.remaining_quantity})
    
    asks = []
    for price, ts, order in self.asks[:levels]:
        if order.status == OrderStatus.OPEN:
            asks.append({'price': price, 'size': order.remaining_quantity})
    
    return {'bids': bids, 'asks': asks}

def get_vwap(self) -> float:
    """Calculate Volume Weighted Average Price"""
    if not self.trades:
        return 0
    
    total_value = sum(trade.price * trade.quantity for trade in self.trades[-100:])
    total_volume = sum(trade.quantity for trade in self.trades[-100:])
    
    return total_value / total_volume if total_volume > 0 else 0

def get_order_book_imbalance(self) -> float:
    """Calculate bid-ask imbalance ratio"""
    bid_volume = sum(order.remaining_quantity for _, _, order in self.bids[:10])
    ask_volume = sum(order.remaining_quantity for _, _, order in self.asks[:10])
    
    if bid_volume + ask_volume == 0:
        return 0
    
    return (bid_volume - ask_volume) / (bid_volume + ask_volume)