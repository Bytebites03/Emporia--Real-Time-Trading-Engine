"""
Smart Order Routing System
Routes orders to multiple liquidity sources for best execution
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class ExchangeType(Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"
    BYBIT = "bybit"

@dataclass
class LiquiditySource:
    exchange: ExchangeType
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    latency_ms: int
    fee_rate: float
    
class SmartOrderRouter:
    """Routes orders to best available liquidity source"""
    
    def __init__(self):
        self.sources: Dict[ExchangeType, LiquiditySource] = {}
        self.historical_latency = {}
        
    async def fetch_liquidity(self, exchange: ExchangeType) -> Optional[LiquiditySource]:
        """Fetch liquidity data from exchange (simulated)"""
        # In production, connect to real exchange APIs
        # This is a simulation
        await asyncio.sleep(0.001)  # Simulate network latency
        
        # Simulated data
        base_price = 50000
        sources = {
            ExchangeType.BINANCE: LiquiditySource(
                exchange=ExchangeType.BINANCE,
                bid=base_price - 50,
                ask=base_price + 50,
                bid_size=10,
                ask_size=10,
                latency_ms=50,
                fee_rate=0.001
            ),
            ExchangeType.COINBASE: LiquiditySource(
                exchange=ExchangeType.COINBASE,
                bid=base_price - 48,
                ask=base_price + 52,
                bid_size=8,
                ask_size=8,
                latency_ms=75,
                fee_rate=0.0015
            ),
            ExchangeType.KRAKEN: LiquiditySource(
                exchange=ExchangeType.KRAKEN,
                bid=base_price - 52,
                ask=base_price + 48,
                bid_size=12,
                ask_size=12,
                latency_ms=60,
                fee_rate=0.0012
            )
        }
        
        return sources.get(exchange)
    
    async def get_all_liquidity(self) -> List[LiquiditySource]:
        """Get liquidity from all exchanges"""
        tasks = [self.fetch_liquidity(ex) for ex in ExchangeType]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
    
    def get_best_bid(self, sources: List[LiquiditySource]) -> Optional[LiquiditySource]:
        """Get source with highest bid"""
        if not sources:
            return None
        return max(sources, key=lambda x: x.bid)
    
    def get_best_ask(self, sources: List[LiquiditySource]) -> Optional[LiquiditySource]:
        """Get source with lowest ask"""
        if not sources:
            return None
        return min(sources, key=lambda x: x.ask)
    
    async def route_order(self, side: str, quantity: float) -> Dict:
        """Route order to best available source"""
        sources = await self.get_all_liquidity()
        
        if side == "buy":
            best = self.get_best_ask(sources)
            if best:
                estimated_cost = quantity * best.ask * (1 + best.fee_rate)
                return {
                    "exchange": best.exchange.value,
                    "price": best.ask,
                    "total_cost": estimated_cost,
                    "fees": estimated_cost * best.fee_rate,
                    "latency_ms": best.latency_ms
                }
        else:  # sell
            best = self.get_best_bid(sources)
            if best:
                estimated_proceeds = quantity * best.bid * (1 - best.fee_rate)
                return {
                    "exchange": best.exchange.value,
                    "price": best.bid,
                    "total_proceeds": estimated_proceeds,
                    "fees": quantity * best.bid * best.fee_rate,
                    "latency_ms": best.latency_ms
                }
        
        return {"error": "No liquidity sources available"}
    
    async def route_slice_order(self, side: str, quantity: float, slices: int = 3) -> List[Dict]:
        """Slice order across multiple venues"""
        sources = await self.get_all_liquidity()
        
        if not sources:
            return []
        
        # Sort sources by price
        if side == "buy":
            sources.sort(key=lambda x: x.ask)
        else:
            sources.sort(key=lambda x: x.bid, reverse=True)
        
        slice_size = quantity / slices
        routes = []
        
        for i, source in enumerate(sources[:slices]):
            routes.append({
                "exchange": source.exchange.value,
                "quantity": slice_size,
                "price": source.ask if side == "buy" else source.bid,
                "estimated_value": slice_size * (source.ask if side == "buy" else source.bid),
                "fee": slice_size * (source.ask if side == "buy" else source.bid) * source.fee_rate
            })
        
        return routes

# Global instance
sor = SmartOrderRouter()