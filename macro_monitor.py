import os
import time
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from pybit.unified_trading import HTTP

# --- ПОЛУЧЕНИЕ ТОКЕНОВ ИЗ ОКРУЖЕНИЯ (ENV) ---
# Скрипт возьмет те же переменные, что прописаны в твоей системе/лайв-боте
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MA_WINDOW = 50
Z_THRESHOLD = 3.0  # Порог паники (3 сигмы)

# Ключи Bybit не нужны, так как мы берем только публичные рыночные данные
session = HTTP(testnet=False, domain="bytick")

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠ Ошибка: Переменные TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не найдены в env!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def get_crypto_gold_data():
    """Получаем данные по Золоту и Биткоину с Bybit"""
    try:
        # Золото
        g_klines = session.get_kline(category="linear", symbol="XAUUSDT", interval="15", limit=MA_WINDOW + 5)
        gdf = pd.DataFrame(g_klines['result']['list'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        gdf = gdf.iloc[::-1].reset_index(drop=True)
        gdf['close'] = gdf['close'].astype(float)
        
        # Биткоин
        b_klines = session.get_kline(category="linear", symbol="BTCUSDT", interval="15", limit=MA_WINDOW + 5)
        bdf = pd.DataFrame(b_klines['result']['list'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        bdf = bdf.iloc[::-1].reset_index(drop=True)
        bdf['close'] = bdf['close'].astype(float)
        
        return gdf, bdf
    except Exception as e:
        print(f"Ошибка получения данных с Bybit: {e}")
        return None, None

def get_dxy_data():
    """Получаем данные Индекса Доллара (DXY) из Yahoo Finance"""
    try:
        dxy = yf.Ticker("DX-Y.NYB")
        df = dxy.history(interval="15m", period="5d")
        if df.empty:
            return None
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        print(f"Ошибка получения DXY: {e}")
        return None

def calculate_z_score(df):
    """Считаем Z-Score для последней закрытой свечи"""
    df['ma'] = df['close'].rolling(window=MA_WINDOW).mean()
    df['std'] = df['close'].rolling(window=MA_WINDOW).std()
    last_row = df.dropna().iloc[-1]
    z_score = (last_row['close'] - last_row['ma']) / last_row['std']
    return z_score, last_row['close']

print("🚀 Макро-монитор запущен и следит за env-переменными...")

last_signal_time = 0

while True:
    current_time = time.time()
    gdf, bdf = get_crypto_gold_data()
    ddf = get_dxy_data()
    
    if gdf is not None and bdf is not None and ddf is not None:
        z_gold, price_gold = calculate_z_score(gdf)
        z_btc, price_btc = calculate_z_score(bdf)
        z_dxy, price_dxy = calculate_z_score(ddf)
        
        print(f"⏱ Проверка | Z_Gold: {z_gold:.2f} | Z_BTC: {z_btc:.2f} | Z_DXY: {z_dxy:.2f}")
        
        # Системный шум: сработка по 2 и более активам одновременно
        condition_met = (abs(z_gold) >= Z_THRESHOLD) + (abs(z_btc) >= Z_THRESHOLD) + (abs(z_dxy) >= Z_THRESHOLD)
        
        if condition_met >= 2 and (current_time - last_signal_time > 7200):
            
            str_gold = "РЕЗКИЙ ВЗЛЕТ 📈" if z_gold > 0 else "ЖЕСТКИЙ ПРОЛИВ 📉"
            str_btc = "РЕЗКИЙ ВЗЛЕТ 📈" if z_btc > 0 else "ЖЕСТКИЙ ПРОЛИВ 📉"
            str_dxy = "РЕЗКИЙ ВЗЛЕТ 📈" if z_dxy > 0 else "ЖЕСТКИЙ ПРОЛИВ 📉"
            
            msg = (
                "🚨 [МАКРО-АЛЕРТ] ОБНАРУЖЕНА СИСТЕМНАЯ ПАНИКА РЫНКА\n\n"
                "Мой алгоритм зафиксировал одновременное аномальное отклонение (Z-Score ≥ 3.0) "
                "на ключевых рынках. Капитал панически переливается из одних активов в другие. "
                "Новостные ленты, скорее всего, еще молчат.\n\n"
                "📊 ТЕКУЩИЕ ДАННЫЕ АНОМАЛИИ:\n"
                f"• 🟡 Золото (XAUUSDT): {str_gold} (Z-Score: {z_gold:.2f})\n"
                f"• 🌐 Биткоин (BTCUSDT): {str_btc} (Z-Score: {z_btc:.2f})\n"
                f"• 💵 Индекс Доллара (DXY): {str_dxy} (Z-Score: {z_dxy:.2f})\n\n"
                "⚡️ ВЕРДИКТ: Прямо сейчас происходит крупное макроэкономическое или геополитическое событие. "
                "Умные деньги уже бегут."
            )
            
            send_telegram_message(msg)
            print("🔔 Сигнал паники отправлен в Telegram!")
            last_signal_time = current_time
            
    time.sleep(300)