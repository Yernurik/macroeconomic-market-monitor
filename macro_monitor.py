import os
import time
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from pybit.unified_trading import HTTP

# --- ENVIRONMENT VARIABLES SETUP (ENV) ---
# The script will fetch the variables directly from your system environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MA_WINDOW = 50
Z_THRESHOLD = 3.0  # Panic Threshold (3 Sigmas)

# Bybit API keys are not required since we only fetch public market data
session = HTTP(testnet=False, domain="bytick")

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠ Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not found in environment variables!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def get_crypto_gold_data():
    """Fetches Gold and Bitcoin market data from Bybit"""
    try:
        # Gold Data
        g_klines = session.get_kline(category="linear", symbol="XAUUSDT", interval="15", limit=MA_WINDOW + 5)
        gdf = pd.DataFrame(g_klines['result']['list'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        gdf = gdf.iloc[::-1].reset_index(drop=True)
        gdf['close'] = gdf['close'].astype(float)
        
        # Bitcoin Data
        b_klines = session.get_kline(category="linear", symbol="BTCUSDT", interval="15", limit=MA_WINDOW + 5)
        bdf = pd.DataFrame(b_klines['result']['list'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        bdf = bdf.iloc[::-1].reset_index(drop=True)
        bdf['close'] = bdf['close'].astype(float)
        
        return gdf, bdf
    except Exception as e:
        print(f"Error fetching data from Bybit: {e}")
        return None, None

def get_dxy_data():
    """Fetches Dollar Index (DXY) data from Yahoo Finance"""
    try:
        dxy = yf.Ticker("DX-Y.NYB")
        df = dxy.history(interval="15m", period="5d")
        if df.empty:
            return None
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        print(f"Error fetching DXY data: {e}")
        return None

def calculate_z_score(df):
    """Calculates Z-Score for the last closed candle"""
    df['ma'] = df['close'].rolling(window=MA_WINDOW).mean()
    df['std'] = df['close'].rolling(window=MA_WINDOW).std()
    last_row = df.dropna().iloc[-1]
    z_score = (last_row['close'] - last_row['ma']) / last_row['std']
    return z_score, last_row['close']


print("🚀 Macro Monitor is running and listening to environment variables...")

last_signal_time = 0

while True:
    current_time = time.time()
    gdf, bdf = get_crypto_gold_data()
    ddf = get_dxy_data()
    
    if gdf is not None and bdf is not None and ddf is not None:
        z_gold, price_gold = calculate_z_score(gdf)
        z_btc, price_btc = calculate_z_score(bdf)
        z_dxy, price_dxy = calculate_z_score(ddf)
        
        print(f"⏱ Check | Z_Gold: {z_gold:.2f} | Z_BTC: {z_btc:.2f} | Z_DXY: {z_dxy:.2f}")
        
        # Systemic risk check: Trigger if 2 or more assets cross the threshold simultaneously
        condition_met = (abs(z_gold) >= Z_THRESHOLD) + (abs(z_btc) >= Z_THRESHOLD) + (abs(z_dxy) >= Z_THRESHOLD)
        
        if condition_met >= 2 and (current_time - last_signal_time > 7200):
            
            str_gold = "SHARP SPIKE 📈" if z_gold > 0 else "HEAVY FLUSH 📉"
            str_btc = "SHARP SPIKE 📈" if z_btc > 0 else "HEAVY FLUSH 📉"
            str_dxy = "SHARP SPIKE 📈" if z_dxy > 0 else "HEAVY FLUSH 📉"
            
            msg = (
                "🚨 [MACRO ALERT] SYSTEMIC MARKET PANIC DETECTED\n\n"
                "The algorithm has detected a simultaneous abnormal deviation (Z-Score ≥ 3.0) "
                "across core global markets. Capital is aggressively rotating out of risk parameters. "
                "Mainstream news feeds are likely lagging behind this shift.\n\n"
                "📊 CURRENT ANOMALY DATA:\n"
                f"• 🟡 Gold (XAUUSDT): {str_gold} (Z-Score: {z_gold:.2f})\n"
                f"• 🌐 Bitcoin (BTCUSDT): {str_btc} (Z-Score: {z_btc:.2f})\n"
                f"• 💵 Dollar Index (DXY): {str_dxy} (Z-Score: {z_dxy:.2f})\n\n"
                "⚡ VERDICT: A major macroeconomic or geopolitical catalyst is developing in real-time. "
                "Smart money is moving."
            )
            
            send_telegram_message(msg)
            print("🔔 Panic signal dispatched to Telegram!")
            last_signal_time = current_time
            
    time.sleep(300)
