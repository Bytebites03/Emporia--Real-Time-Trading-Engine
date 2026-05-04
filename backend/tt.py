import requests
import json

# Login
print("=" * 50)
print("Testing Profit/Loss Predictor")
print("=" * 50)
print()

try:
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "admin", "password": "admin123"}
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        exit()

    token = login_response.json()['access_token']
    print(f"✅ Logged in successfully")
    print()
except Exception as e:
    print(f"❌ Backend not running. Please start backend first: python app.py")
    print(f"Error: {e}")
    exit()

headers = {"Authorization": f"Bearer {token}"}

# Test 1: Entry Prediction
print("=" * 50)
print("Test 1: Entry Prediction")
print("=" * 50)

try:
    response = requests.post(
        "http://localhost:8000/predict/entry",
        params={"symbol": "BTC/USD", "entry_price": 48000, "quantity": 0.1},
        headers=headers
    )

    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Symbol: {data.get('symbol', 'N/A')}")
    print(f"Current Price: ${data.get('current_price', 'N/A')}")
    print(f"Entry Price: ${data.get('entry_price', 'N/A')}")
    print(f"Total Investment: ${data.get('total_investment', 'N/A')}")
    print()
    print("Predictions:")
    
    predictions = data.get('predictions', {})
    print(f"  Optimistic: +${predictions.get('optimistic', {}).get('profit', 0)} ({predictions.get('optimistic', {}).get('return_percent', 0)}%)")
    print(f"  Likely: +${predictions.get('likely', {}).get('profit', 0)} ({predictions.get('likely', {}).get('return_percent', 0)}%)")
    print(f"  Pessimistic: -${predictions.get('pessimistic', {}).get('loss', 0)} ({predictions.get('pessimistic', {}).get('loss_percent', 0)}%)")
    print()
    
    analysis = data.get('analysis', {})
    print(f"Trend: {analysis.get('trend', 'N/A')}")
    print(f"Probability of Profit: {analysis.get('probability_of_profit', 0)}%")
    print(f"Risk Level: {analysis.get('risk_level', 'N/A')}")
    print(f"Recommendation: {data.get('recommendation', 'N/A')}")
    print()

except Exception as e:
    print(f"Error: {e}")
    print("Response may have different structure")
    print(f"Raw response: {data if 'data' in locals() else 'No response'}")

# Test 2: Risk-Reward Calculation
print("=" * 50)
print("Test 2: Risk-Reward Calculation")
print("=" * 50)

try:
    response2 = requests.post(
        "http://localhost:8000/predict/risk-reward",
        params={"entry_price": 50000, "stop_loss": 49000, "take_profit": 52000, "quantity": 1}
    )

    data2 = response2.json()
    print(f"Entry: ${data2.get('entry_price', 'N/A')}")
    print(f"Stop Loss: ${data2.get('stop_loss', 'N/A')}")
    print(f"Take Profit: ${data2.get('take_profit', 'N/A')}")
    print(f"Risk Amount: ${data2.get('risk_amount', 'N/A')}")
    print(f"Reward Amount: ${data2.get('reward_amount', 'N/A')}")
    print(f"Risk-Reward Ratio: 1:{data2.get('risk_reward_ratio', 'N/A')}")
    print(f"Assessment: {data2.get('assessment', 'N/A')}")
    print(f"Recommendation: {data2.get('recommendation', 'N/A')}")
    print(f"Win Rate Needed: {data2.get('win_rate_needed', 'N/A')}%")
    print()

except Exception as e:
    print(f"Error: {e}")

# Test 3: Market Sentiment
print("=" * 50)
print("Test 3: Market Sentiment")
print("=" * 50)

try:
    response3 = requests.get(
        "http://localhost:8000/predict/sentiment/BTC/USD",
        headers=headers
    )

    data3 = response3.json()
    print(f"Symbol: {data3.get('symbol', 'N/A')}")
    print(f"Current Price: ${data3.get('current_price', 'N/A')}")
    print(f"Sentiment: {data3.get('sentiment', 'N/A')}")
    print(f"Score: {data3.get('score', 'N/A')}/100")
    print(f"Action: {data3.get('action', 'N/A')}")
    
    metrics = data3.get('metrics', {})
    print(f"1h Change: {metrics.get('change_1h', 'N/A')}%")
    print(f"24h Change: {metrics.get('change_24h', 'N/A')}%")
    print(f"Momentum: {metrics.get('momentum', 'N/A')}%")
    print()

except Exception as e:
    print(f"Error: {e}")

print("=" * 50)
print("✅ Tests completed!")
print("=" * 50)