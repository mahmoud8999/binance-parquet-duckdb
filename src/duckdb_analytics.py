import duckdb


class ParquetAnalysis:

    def __init__(self):
        self.connection = duckdb.connect(database=":memory:")

        # View for reading Parquet files
        self.connection.execute("""
            CREATE VIEW market_data AS
            SELECT
                regexp_extract(filename, 'Data/([^/]+)/', 1) AS symbol,
                * EXCLUDE (filename)
            FROM read_parquet(
                'Data/*/*.parquet',
                filename = true
            )
        """)

        # View for calculating hourly returns
        self.connection.execute("""
            CREATE VIEW hourly_returns AS

            WITH previous_prices AS (
                SELECT
                    symbol,
                    open_time,
                    close,

                    LAG(close) OVER (
                        PARTITION BY symbol
                        ORDER BY open_time
                    ) AS previous_close,

                    LAG(open_time) OVER (
                        PARTITION BY symbol
                        ORDER BY open_time
                    ) AS previous_time

                FROM market_data
            )

            SELECT
                symbol,
                open_time,
                close,
                previous_close,

                CASE
                    WHEN open_time - previous_time = INTERVAL '1 hour'
                         AND previous_close > 0
                    THEN
                        ((close - previous_close) / previous_close) * 100
                    ELSE NULL
                END AS hourly_return

            FROM previous_prices
        """)

    # ---------------------------------------------------------
    # 1. Count Records
    # ---------------------------------------------------------

    def count_records(self):
        result = self.connection.execute("""
            SELECT
                symbol,
                COUNT(*) AS total_records
            FROM market_data
            GROUP BY symbol
            ORDER BY symbol
        """).df()

        print("\n========== TOTAL RECORDS ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 2. Check NULL Values
    # ---------------------------------------------------------

    def check_null_values(self):
        result = self.connection.execute("""
            SELECT
                symbol,

                COUNT(*) FILTER (
                    WHERE open_time IS NULL
                ) AS open_time_nulls,

                COUNT(*) FILTER (
                    WHERE open IS NULL
                ) AS open_nulls,

                COUNT(*) FILTER (
                    WHERE high IS NULL
                ) AS high_nulls,

                COUNT(*) FILTER (
                    WHERE low IS NULL
                ) AS low_nulls,

                COUNT(*) FILTER (
                    WHERE close IS NULL
                ) AS close_nulls,

                COUNT(*) FILTER (
                    WHERE volume IS NULL
                ) AS volume_nulls,

                COUNT(*) FILTER (
                    WHERE close_time IS NULL
                ) AS close_time_nulls,

                COUNT(*) FILTER (
                    WHERE quote_asset_volume IS NULL
                ) AS quote_volume_nulls,

                COUNT(*) FILTER (
                    WHERE number_of_trades IS NULL
                ) AS trades_nulls,

                COUNT(*) FILTER (
                    WHERE taker_buy_base_asset_volume IS NULL
                ) AS taker_base_nulls,

                COUNT(*) FILTER (
                    WHERE taker_buy_quote_asset_volume IS NULL
                ) AS taker_quote_nulls,

                COUNT(*) FILTER (
                    WHERE ignore IS NULL
                ) AS ignore_nulls

            FROM market_data
            GROUP BY symbol
            ORDER BY symbol
        """).df()

        print("\n========== NULL VALUE CHECK ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 3. Check Timestamps
    # ---------------------------------------------------------

    def check_timestamps(self):
        result = self.connection.execute("""
            SELECT
                symbol,
                MIN(open_time) AS earliest_timestamp,
                MAX(open_time) AS latest_timestamp
            FROM market_data
            GROUP BY symbol
            ORDER BY symbol
        """).df()

        print("\n========== TIMESTAMP COVERAGE ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 4. Check Missing Hourly Candles
    # ---------------------------------------------------------

    def check_missing_data(self):
        result = self.connection.execute("""
            WITH previous_candles AS (
                SELECT
                    symbol,
                    open_time,

                    LAG(open_time) OVER (
                        PARTITION BY symbol
                        ORDER BY open_time
                    ) AS previous_time

                FROM market_data
            )

            SELECT
                symbol,
                previous_time,
                open_time,

                open_time - previous_time AS time_difference,

                date_diff(
                    'hour',
                    previous_time,
                    open_time
                ) - 1 AS missing_candles

            FROM previous_candles

            WHERE
                open_time - previous_time > INTERVAL '1 hour'

            ORDER BY symbol, open_time
        """).df()

        print("\n========== MISSING HOURLY CANDLES ==========")

        if result.empty:
            print("No missing hourly candles detected.")
        else:
            print(result.to_string(index=False))

            print(
                "\nTotal missing candles:",
                result["missing_candles"].sum()
            )

    # ---------------------------------------------------------
    # 5. Validate OHLCV
    # ---------------------------------------------------------

    def check_ohlcv(self):
        result = self.connection.execute("""
            SELECT
                symbol,
                open_time,
                open,
                high,
                low,
                close,
                volume,
                number_of_trades

            FROM market_data

            WHERE
                high < open
                OR high < close
                OR high < low
                OR low > open
                OR low > close

                OR open <= 0
                OR high <= 0
                OR low <= 0
                OR close <= 0

                OR volume < 0
                OR quote_asset_volume < 0
                OR taker_buy_base_asset_volume < 0
                OR taker_buy_quote_asset_volume < 0

                OR number_of_trades < 0

            ORDER BY symbol, open_time
        """).df()

        print("\n========== OHLCV VALIDATION ==========")

        if result.empty:
            print("No invalid OHLCV records detected.")
        else:
            print(result.to_string(index=False))
            print("\nTotal invalid records:", len(result))

    # ---------------------------------------------------------
    # 6. Check Duplicate Timestamps
    # ---------------------------------------------------------

    def duplicate_timestamps(self):
        result = self.connection.execute("""
            SELECT
                symbol,
                open_time,
                COUNT(*) AS duplicate_count

            FROM market_data

            GROUP BY symbol, open_time

            HAVING COUNT(*) > 1

            ORDER BY symbol, open_time
        """).df()

        print("\n========== DUPLICATE TIMESTAMPS ==========")

        if result.empty:
            print("No duplicate timestamps detected.")
        else:
            print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 7. Calculate Hourly Returns
    # ---------------------------------------------------------

    def calculate_hourly_returns(self):
        result = self.connection.execute("""
            WITH ranked_returns AS (
                SELECT
                    symbol,
                    open_time,
                    close,
                    previous_close,
                    hourly_return,

                    ROW_NUMBER() OVER (
                        PARTITION BY symbol
                        ORDER BY open_time DESC
                    ) AS row_number

                FROM hourly_returns
            )

            SELECT
                symbol,
                open_time,
                close,
                previous_close,
                hourly_return

            FROM ranked_returns

            WHERE row_number <= 10

            ORDER BY symbol, open_time DESC
        """).df()

        print("\n========== HOURLY RETURNS (%) ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 8. Calculate Rolling 24-Hour Volatility
    # ---------------------------------------------------------

    def calculate_24h_volatility(self):
        result = self.connection.execute("""
            WITH rolling_volatility AS (
                SELECT
                    symbol,
                    open_time,
                    hourly_return,

                    CASE
                        WHEN COUNT(hourly_return) OVER (
                            PARTITION BY symbol
                            ORDER BY open_time
                            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
                        ) = 24

                        THEN STDDEV_SAMP(hourly_return) OVER (
                            PARTITION BY symbol
                            ORDER BY open_time
                            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
                        )

                        ELSE NULL
                    END AS volatility_24h

                FROM hourly_returns
            ),

            ranked_results AS (
                SELECT
                    symbol,
                    open_time,
                    volatility_24h,

                    ROW_NUMBER() OVER (
                        PARTITION BY symbol
                        ORDER BY open_time DESC
                    ) AS row_number

                FROM rolling_volatility
            )

            SELECT
                symbol,
                open_time,
                volatility_24h

            FROM ranked_results

            WHERE row_number <= 10

            ORDER BY symbol, open_time DESC
        """).df()

        print("\n========== ROLLING 24-HOUR VOLATILITY (%) ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # 9. Calculate Rolling 7-Day Volatility
    # ---------------------------------------------------------

    def calculate_7d_volatility(self):
        result = self.connection.execute("""
            WITH rolling_volatility AS (
                SELECT
                    symbol,
                    open_time,
                    hourly_return,

                    CASE
                        WHEN COUNT(hourly_return) OVER (
                            PARTITION BY symbol
                            ORDER BY open_time
                            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
                        ) = 168

                        THEN STDDEV_SAMP(hourly_return) OVER (
                            PARTITION BY symbol
                            ORDER BY open_time
                            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
                        )

                        ELSE NULL
                    END AS volatility_7d

                FROM hourly_returns
            ),

            ranked_results AS (
                SELECT
                    symbol,
                    open_time,
                    volatility_7d,

                    ROW_NUMBER() OVER (
                        PARTITION BY symbol
                        ORDER BY open_time DESC
                    ) AS row_number

                FROM rolling_volatility
            )

            SELECT
                symbol,
                open_time,
                volatility_7d

            FROM ranked_results

            WHERE row_number <= 10

            ORDER BY symbol, open_time DESC
        """).df()

        print("\n========== ROLLING 7-DAY VOLATILITY (%) ==========")
        print(result.to_string(index=False))

    # ---------------------------------------------------------
    # Run All Analytics
    # ---------------------------------------------------------

    def run_all(self):
        self.count_records()
        self.check_timestamps()
        self.check_missing_data()
        self.check_null_values()
        self.check_ohlcv()
        self.duplicate_timestamps()
        self.calculate_hourly_returns()
        self.calculate_24h_volatility()
        self.calculate_7d_volatility()
