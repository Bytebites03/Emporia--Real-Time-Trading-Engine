from er_database import db

class RiskManager:
    def __init__(self):
        pass
    
    def get_balance(self, user_id: str):
        portfolio = db.get_portfolio(user_id)
        if portfolio:
            return type('Balance', (), {
                'cash': portfolio['cash_balance'],
                'crypto': portfolio['crypto_balance']
            })()
        return type('Balance', (), {'cash': 10000, 'crypto': 1})()
    
    def validate_order(self, user_id: str, side: str, price: float, quantity: float):
        balance = self.get_balance(user_id)
        
        if side == "buy":
            required_cash = price * quantity
            if balance.cash < required_cash:
                return False, f"Insufficient cash: need ${required_cash:.2f}, have ${balance.cash:.2f}"
        else:
            if balance.crypto < quantity:
                return False, f"Insufficient crypto: need {quantity}, have {balance.crypto}"
        
        if quantity > 10:
            return False, "Order size exceeds maximum (10)"
        
        return True, "OK"
    
    def update_balance(self, user_id: str, side: str, price: float, quantity: float):
        if side == "buy":
            db.update_portfolio(user_id, -price * quantity, quantity, price * quantity)
        else:
            db.update_portfolio(user_id, price * quantity, -quantity, price * quantity)