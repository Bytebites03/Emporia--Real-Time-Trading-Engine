"""
Profit/Loss Predictor Module for Trading Engine
"""

import random
import numpy as np
from datetime import datetime
from typing import Dict, List
from collections import deque

class ProfitLossPredictor:
    def __init__(self):
        self.price_history = {}
        
    def add_price_data(self, symbol: str, price: float):
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=100)
        self.price_history[symbol].append(price)
    
    def predict_entry(self, symbol: str, entry_price: float, quantity: float) -> Dict:
        """Predict profit/loss for a potential trade"""
        
        # Get historical prices
        prices = list(self.price_history.get(symbol, []))
        
        # Get current price from live_prices or use entry_price
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        try:
            from app import live_prices
            current_price = live_prices.get(symbol, entry_price)
        except:
            current_price = entry_price
        
        investment = entry_price * quantity
        
        # Add current price to history if not already there
        if current_price not in prices:
            self.add_price_data(symbol, current_price)
            prices = list(self.price_history.get(symbol, []))
        
        # If we have historical data, calculate based on it
        if len(prices) >= 5:
            # Calculate statistics from historical data
            avg_price = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
            volatility = np.std(prices[-20:]) if len(prices) >= 20 else (current_price * 0.01)
            
            # Calculate potential movements
            optimistic_move = volatility * 2.5
            likely_move = volatility * 1.2
            pessimistic_move = volatility * 1.5
            
            optimistic_price = current_price + optimistic_move
            likely_price = current_price + likely_move
            pessimistic_price = current_price - pessimistic_move
            
            optimistic_profit = (optimistic_price - entry_price) * quantity
            likely_profit = (likely_price - entry_price) * quantity
            pessimistic_loss = (pessimistic_price - entry_price) * quantity
            
            # Calculate trend direction
            trend = "Upward" if current_price > avg_price else "Downward"
            
            # Calculate probability based on trend strength
            trend_strength = abs(current_price - avg_price) / avg_price
            if trend == "Upward":
                probability = 50 + min(40, trend_strength * 100)
            else:
                probability = 50 - min(40, trend_strength * 100)
            probability = max(30, min(70, probability))
            
            # Risk level based on volatility
            daily_volatility_pct = (volatility / current_price) * 100
            if daily_volatility_pct < 0.8:
                risk_level = "Low"
            elif daily_volatility_pct < 1.5:
                risk_level = "Medium"
            else:
                risk_level = "High"
            
            # Recommendation
            if probability > 60 and likely_profit > 0:
                recommendation = "BUY"
            elif probability > 55:
                recommendation = "CONSIDER"
            elif probability > 45:
                recommendation = "HOLD"
            else:
                recommendation = "AVOID"
            
            return {
                "success": True,
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "entry_price": entry_price,
                "quantity": quantity,
                "total_investment": round(investment, 2),
                "predictions": {
                    "optimistic": {
                        "profit": round(optimistic_profit, 2),
                        "return_percent": round((optimistic_profit / investment) * 100, 2) if investment > 0 else 0
                    },
                    "likely": {
                        "profit": round(likely_profit, 2),
                        "return_percent": round((likely_profit / investment) * 100, 2) if investment > 0 else 0
                    },
                    "pessimistic": {
                        "loss": round(abs(pessimistic_loss), 2),
                        "loss_percent": round((abs(pessimistic_loss) / investment) * 100, 2) if investment > 0 else 0
                    }
                },
                "analysis": {
                    "volatility": round(volatility, 2),
                    "daily_volatility_percent": round(daily_volatility_pct, 2),
                    "trend": trend,
                    "probability_of_profit": round(probability, 1),
                    "risk_level": risk_level
                },
                "recommendation": recommendation,
                "timestamp": datetime.now().isoformat()
            }
        
        # Default prediction when insufficient historical data
        return {
            "success": True,
            "symbol": symbol,
            "current_price": round(current_price, 2),
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
                "volatility": round(current_price * 0.01, 2),
                "daily_volatility_percent": 1.0,
                "trend": "Neutral",
                "probability_of_profit": 55.0,
                "risk_level": "Medium"
            },
            "recommendation": "CONSIDER",
            "message": "Building price history for better predictions",
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_risk_reward(self, entry: float, stop_loss: float, take_profit: float, quantity: float) -> Dict:
        """Calculate risk-reward ratio"""
        
        risk_amount = abs(entry - stop_loss) * quantity
        reward_amount = abs(take_profit - entry) * quantity
        ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        if ratio >= 3:
            assessment = "Excellent"
            recommendation = "STRONG ENTRY"
        elif ratio >= 2:
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
            "entry_price": entry,
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
    
    def get_market_sentiment(self, symbol: str, current_price: float) -> Dict:
        """Get market sentiment based on recent price action"""
        
        prices = list(self.price_history.get(symbol, []))
        
        # Add current price
        if current_price not in prices:
            self.add_price_data(symbol, current_price)
            prices = list(self.price_history.get(symbol, []))
        
        if len(prices) < 5:
            return {
                "success": True,
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "sentiment": "Neutral",
                "score": 50,
                "action": "Wait for more data",
                "color": "gray",
                "metrics": {
                    "change_1h": 0,
                    "change_24h": 0,
                    "momentum": 0
                },
                "message": "Building price history for sentiment analysis"
            }
        
        # Calculate metrics
        price_1h_ago = prices[-12] if len(prices) >= 12 else prices[0]
        price_24h_ago = prices[0]
        current = prices[-1]
        
        change_1h = ((current - price_1h_ago) / price_1h_ago) * 100 if price_1h_ago != 0 else 0
        change_24h = ((current - price_24h_ago) / price_24h_ago) * 100 if price_24h_ago != 0 else 0
        
        # Calculate momentum
        recent_prices = prices[-10:] if len(prices) >= 10 else prices
        if len(recent_prices) >= 2:
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        else:
            momentum = 0
        
        # Determine sentiment score (0-100)
        score = 50
        
        if change_1h > 0.5:
            score += 15
        elif change_1h > 0:
            score += 5
        elif change_1h < -0.5:
            score -= 15
        elif change_1h < 0:
            score -= 5
        
        if change_24h > 2:
            score += 20
        elif change_24h > 0:
            score += 10
        elif change_24h < -2:
            score -= 20
        elif change_24h < 0:
            score -= 10
        
        if momentum > 0:
            score += 10
        else:
            score -= 10
        
        score = max(0, min(100, score))
        
        # Determine sentiment
        if score >= 70:
            sentiment = "Very Bullish"
            action = "Aggressive Buy"
            color = "green"
        elif score >= 55:
            sentiment = "Bullish"
            action = "Buy on Dips"
            color = "lightgreen"
        elif score >= 45:
            sentiment = "Neutral"
            action = "Hold / Wait"
            color = "gray"
        elif score >= 30:
            sentiment = "Bearish"
            action = "Reduce Position"
            color = "orange"
        else:
            sentiment = "Very Bearish"
            action = "Avoid / Sell"
            color = "red"
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": round(current, 2),
            "sentiment": sentiment,
            "score": round(score, 1),
            "action": action,
            "color": color,
            "metrics": {
                "change_1h": round(change_1h, 2),
                "change_24h": round(change_24h, 2),
                "momentum": round(momentum, 2)
            }
        }

# Create instance
predictor = ProfitLossPredictor()