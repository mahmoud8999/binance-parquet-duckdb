from src.binance_client import BinanceClient
from src.parquet_processor import ParquetProcessor
from src.duckdb_analytics import ParquetAnalysis

import config

def fetch_and_store():
    client = BinanceClient()
    
    print("=" * 60)
    print("BINANCE HISTORICAL OHLCV DATA INGESTION")
    print("=" * 60)
    
    print(f"Start Date : {config.BINANCE_START_TIME}")
    print(f"End Date   : {config.BINANCE_END_TIME}")
    print(f"Interval   : {config.BINANCE_INTERVAL}")
    print(f"Symbols    : {len(config.BINANCE_SYMBOLS)}")
    print("=" * 60)
    
    for symbol in config.BINANCE_SYMBOLS:

        print(f"\n[{symbol}] Starting historical data retrieval...")

        historical_data = client.get_historical_klines(symbol)
        
        parquet = ParquetProcessor(historical_data)
        
        parquet.define_schema()
        parquet.create_batch_reader()
        parquet.write_parquet_dataset()

    print("\n" + "=" * 60)
    print("ALL SYMBOLS PROCESSED SUCCESSFULLY")
    print("=" * 60)
    
def analyze_data():

    db_client = ParquetAnalysis()
    db_client.run_all()

def main():

    fetch_and_store()
    analyze_data()    

if __name__ == "__main__":
    main()
