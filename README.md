# Binance Parquet & DuckDB Analytics

Historical cryptocurrency market data ingestion and analytics pipeline built with Python, Binance REST API, PyArrow, Apache Parquet, and DuckDB.

The project demonstrates how to retrieve historical financial market data, transform it into a columnar format, store it efficiently using Apache Parquet, and perform analytical SQL queries using DuckDB.

## Technologies

- Python
- Binance REST API
- Requests
- PyArrow
- Apache Parquet
- DuckDB
- SQL

## Architecture

```text
Binance REST API
       |
       v
Python (Requests)
       |
       v
Historical OHLCV Data
       |
       v
PyArrow
       |
       v
RecordBatch / RecordBatchReader
       |
       v
Apache Parquet
       |
       v
DuckDB
       |
       v
SQL Analytics
```

## Features

### Historical Market Data Ingestion

- Retrieve historical OHLCV data from Binance REST API.
- Support multiple cryptocurrency trading pairs.
- Configure historical date ranges and candle intervals.
- Handle API pagination for large historical datasets.
- Process API responses in batches.

### Columnar Data Processing

- Define structured schemas using PyArrow.
- Convert API responses into columnar data.
- Create PyArrow RecordBatch objects.
- Use RecordBatchReader for batch-based data processing.
- Write historical market data into Apache Parquet files.

### Parquet Storage

- Store historical OHLCV data in Apache Parquet format.
- Organize data by cryptocurrency trading pair.
- Use columnar storage for efficient analytical queries.

### DuckDB Analytics

- Query Parquet files directly using DuckDB.
- Perform SQL-based historical market data analysis.
- Analyze OHLCV data across multiple trading pairs.
- Identify missing hourly candles using SQL window functions.
- Validate historical data continuity.

## Cryptocurrency Trading Pairs

The project currently processes:

- BTCUSDT
- ETHUSDT
- SOLUSDT
- BNBUSDT

## Dataset

The pipeline retrieves historical hourly OHLCV data.

| Property | Value |
|---|---|
| Data Source | Binance REST API |
| Market | Cryptocurrency Spot |
| Interval | 1 Hour |
| Start Date | 2021-01-01 |
| End Date | 2026-09-29 |
| Storage Format | Apache Parquet |
| Query Engine | DuckDB |

The historical date range and trading pairs can be modified through the project configuration.

## Project Structure

```text
binance-parquet-duckdb/
├── config.py
├── Data/
│   ├── BNBUSDT/
│   │   └── part-0.parquet
│   ├── BTCUSDT/
│   │   └── part-0.parquet
│   ├── ETHUSDT/
│   │   └── part-0.parquet
│   └── SOLUSDT/
│       └── part-0.parquet
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── src/
    ├── binance_client.py
    ├── duckdb_analytics.py
    └── parquet_processor.py
```

## Project Components

### Binance Client

`src/binance_client.py`

Responsible for:

- Communicating with the Binance REST API.
- Retrieving historical OHLCV data.
- Managing API pagination.
- Processing historical data in batches.

### Parquet Processor

`src/parquet_processor.py`

Responsible for:

- Defining the PyArrow schema.
- Converting API data into RecordBatch objects.
- Creating RecordBatchReader objects.
- Writing historical data into Parquet files.

### DuckDB Analytics

`src/duckdb_analytics.py`

Responsible for:

- Querying historical OHLCV data stored in Parquet.
- Executing analytical SQL queries.
- Validating historical candle continuity.
- Detecting missing hourly records.

### Main Application

`main.py`

Coordinates the historical data ingestion and processing pipeline.

## Installation

Clone the repository:

```bash
git clone https://github.com/mahmoud8999/binance-parquet-duckdb.git
```

Navigate to the project directory:

```bash
cd binance-parquet-duckdb
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Configure the trading pairs, date range, and candle interval in `config.py`.

Run the application:

```bash
python main.py
```

The application retrieves historical market data from Binance and writes the processed records into Parquet files.

## Data Quality

Historical market data may contain missing hourly candles.

During development, SQL validation using DuckDB identified several gaps in Binance's historical OHLCV data.

Additional investigation confirmed that missing records were already absent from the Binance REST API responses.

A comparison with Binance's downloadable historical CSV data also confirmed a missing candle on February 11, 2021.

This demonstrates the importance of validating source data before performing financial market analysis.

## Learning Objectives

This project focuses on:

- REST API data ingestion
- API pagination
- Batch processing
- PyArrow schemas
- Columnar data representation
- RecordBatch and RecordBatchReader
- Apache Parquet storage
- SQL analytics with DuckDB
- Historical data quality validation

## Data Source

Historical cryptocurrency market data is provided by Binance.

- [Binance API Documentation](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)
- [Binance Historical Data](https://data.binance.vision/)

## Author

[GitHub — mahmoud8999](https://github.com/mahmoud8999)
