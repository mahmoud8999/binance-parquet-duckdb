import requests
from datetime import datetime, timezone

import config

class BinanceClient():

    def __init__(self):
        self.url = config.BINANCE_URL
        self.data_interval = config.BINANCE_INTERVAL
        self.data_request_limit = config.BINANCE_DATA_LIMIT
        self.timeout_interval = config.REQUEST_TIMEOUT
        self.next_hour = config.BINANCE_NEXT_HOUR
        self.start_date = config.BINANCE_START_TIME
        self.end_date = config.BINANCE_END_TIME
    
    def convert_to_timestamp(self, date_value):
        
        timestamp = int(
            datetime.strptime(date_value, "%Y-%m-%d")
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        
        return timestamp
        
    def get_historical_klines(self, symbol):
    
        start_time = self.convert_to_timestamp(self.start_date)
        end_time = self.convert_to_timestamp(self.end_date)
        
        column_names = [
            "symbol",
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore"
        ]
        
        while True:
        
            params = {
                "symbol": symbol,
                "interval": self.data_interval,
                "startTime": start_time,
                "endTime": end_time - 1,
                "limit": self.data_request_limit 
            }
        
            try:
                response = requests.get(
                                        self.url,
                                        params=params,
                                        timeout=self.timeout_interval
                                    )
            
                response.raise_for_status()
            
                data = response.json()
            
                if not data:
                    break
                    
                for i in range(1, len(data)):
                    previous_time = data[i - 1][0]
                    current_time = data[i][0]

                    if current_time - previous_time != self.next_hour:
                        print(
                            f"WARNING [{symbol}]: "
                            f"Gap detected between "
                            f"{previous_time} and {current_time}"
                        )
                    
                for row in data:
                    row.insert(0, symbol)
                    
                columned_data = dict(zip(column_names, map(list, zip(*data))))
                
                print(f"Symbol: {symbol}")
                print(f"Requested start: {start_time}")
                print(f"First returned candle: {data[0][1]}")
                print(f"Last returned candle: {data[-1][1]}")
                print(f"Records returned: {len(data)}")
                print("-" * 60)
                
                if data[0][1] != start_time:
                    print(
                        f"WARNING: Expected candle at {start_time}, "
                        f"but received {data[0][1]}"
                    )
                
                start_time = data[-1][1] + self.next_hour
                
                yield columned_data
                
                if start_time >= end_time:
                    break
                
            except Exception as e:
                print(f"Error unable to request data: {e}")
                raise
