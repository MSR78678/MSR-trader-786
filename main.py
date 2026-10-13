import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

def analyze_market_data(prices):
    df = pd.DataFrame(prices, columns=['close'])
    df['sma_fast'] = df['close'].rolling(window=9).mean()
    df['sma_slow'] = df['close'].rolling(window=21).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]
    
    if latest['sma_fast'] > latest['sma_slow'] and latest['rsi'] < 70:
        return "BUY", round(latest['close'], 2)
    elif latest['sma_fast'] < latest['sma_slow'] and latest['rsi'] > 30:
        return "SELL", round(latest['close'], 2)
    else:
        return "HOLD", round(latest['close'], 2)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "AI Trading Bot Active"})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'prices' not in data:
        return jsonify({"error": "Invalid format"}), 400
    
    signal, price = analyze_market_data(data['prices'])
    return jsonify({"signal": signal, "price": price}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
