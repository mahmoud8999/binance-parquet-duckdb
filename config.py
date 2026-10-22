from pathlib import Path

BINANCE_URL = "https://api.binance.com/api/v3/klines"
BINANCE_INTERVAL = "1h"
BINANCE_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT"
]
BINANCE_DATA_LIMIT = 1000
BINANCE_NEXT_HOUR = 60*60*1000
BINANCE_START_TIME = "2021-01-01"
BINANCE_END_TIME = "2026-09-30"

REQUEST_TIMEOUT = 30

OUTPUT_DIR = Path(__file__).resolve().parent / "Data"
