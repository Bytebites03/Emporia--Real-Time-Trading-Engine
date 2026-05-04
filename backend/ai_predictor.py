"""
AI Price Prediction using Simple Neural Network
For production, use TensorFlow/PyTorch with CNN
"""

import numpy as np
from typing import List, Dict
from collections import deque
import json

from polars import datetime

class SimpleAIPredictor:
    """Simple AI predictor for price movements"""
    
    def __init__(self):
        self.price_history = deque(maxlen=100)
        self.volume_history = deque(maxlen=100)
        self.predictions = []
        
    def add_market_data(self, price: float, volume: float):
        """Add new market data point"""
        self.price_history.append(price)
        self.volume_history.append(volume)
    
    def calculate_features(self) -> Dict:
        """Calculate technical features for prediction"""
        if len(self.price_history) < 20:
            return {}
        
        prices = list(self.price_history)
        
        # Simple moving averages
        sma_5 = np.mean(prices[-5:])
        sma_10 = np.mean(prices[-10:])
        sma_20 = np.mean(prices[-20:])
        
        # Price momentum
        momentum = (prices[-1] - prices[-5]) / prices[-5] if prices[-5] > 0 else 0
        
        # Volatility
        volatility = np.std(prices[-20:])
        
        # RSI (simplified)
        gains = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i] > prices[i-1]]
        losses = [prices[i-1] - prices[i] for i in range(1, len(prices)) if prices[i] < prices[i-1]]
        avg_gain = np.mean(gains[-14:]) if gains else 0
        avg_loss = np.mean(losses[-14:]) if losses else 1
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'sma_5': sma_5,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'momentum': momentum,
            'volatility': volatility,
            'rsi': rsi,
            'current_price': prices[-1]
        }
    
    def predict_price_movement(self) -> Dict:
        """Predict short-term price movement"""
        features = self.calculate_features()
        
        if not features:
            return {'prediction': 'neutral', 'confidence': 0}
        
        # Simple rule-based prediction
        # In production, this would be a trained neural network
        
        signals = []
        
        # SMA crossover
        if features['sma_5'] > features['sma_20']:
            signals.append(('bullish', 0.3))
        elif features['sma_5'] < features['sma_20']:
            signals.append(('bearish', 0.3))
        
        # Momentum
        if features['momentum'] > 0.02:
            signals.append(('bullish', 0.25))
        elif features['momentum'] < -0.02:
            signals.append(('bearish', 0.25))
        
        # RSI
        if features['rsi'] < 30:
            signals.append(('bullish', 0.35))  # Oversold
        elif features['rsi'] > 70:
            signals.append(('bearish', 0.35))  # Overbought
        
        # Aggregate signals
        bullish_score = sum(weight for signal, weight in signals if signal == 'bullish')
        bearish_score = sum(weight for signal, weight in signals if signal == 'bearish')
        
        if bullish_score > bearish_score:
            prediction = 'bullish'
            confidence = min(0.95, bullish_score)
        elif bearish_score > bullish_score:
            prediction = 'bearish'
            confidence = min(0.95, bearish_score)
        else:
            prediction = 'neutral'
            confidence = 0.5
        
        # Calculate expected move
        expected_move = features.get('volatility', 100) * confidence
        
        return {
            'prediction': prediction,
            'confidence': round(confidence * 100, 1),
            'expected_move_24h': round(expected_move, 2),
            'current_price': features.get('current_price', 0),
            'signals': len(signals),
            'rsi': round(features.get('rsi', 50), 1)
        }
    
    def get_trading_signal(self) -> Dict:
        """Get actionable trading signal"""
        prediction = self.predict_price_movement()
        
        signal = 'HOLD'
        action = None
        
        if prediction['prediction'] == 'bullish' and prediction['confidence'] > 70:
            signal = 'BUY'
            action = {
                'type': 'market',
                'size_percent': 0.2,  # Use 20% of portfolio
                'stop_loss_percent': 2,
                'take_profit_percent': 5
            }
        elif prediction['prediction'] == 'bearish' and prediction['confidence'] > 70:
            signal = 'SELL'
            action = {
                'type': 'market',
                'size_percent': 0.2,
                'stop_loss_percent': 2,
                'take_profit_percent': 5
            }
        
        return {
            'signal': signal,
            'prediction': prediction,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
ai_predictor = SimpleAIPredictor()