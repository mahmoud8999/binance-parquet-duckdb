import pyarrow as pa
import pyarrow.dataset as ds

import config


class ParquetProcessor:

    def __init__(self, column_data):
        self.column_data = column_data
        self.reader = None
        self.column_data_schema = None
        self.output_dir = config.OUTPUT_DIR

    def define_schema(self):

        self.column_data_schema = pa.schema([
            pa.field("symbol", pa.string()),
            pa.field("open_time", pa.timestamp("ms", tz="UTC")),
            pa.field("open", pa.float64()),
            pa.field("high", pa.float64()),
            pa.field("low", pa.float64()),
            pa.field("close", pa.float64()),
            pa.field("volume", pa.float64()),
            pa.field("close_time", pa.timestamp("ms", tz="UTC")),
            pa.field("quote_asset_volume", pa.float64()),
            pa.field("number_of_trades", pa.int64()),
            pa.field("taker_buy_base_asset_volume", pa.float64()),
            pa.field("taker_buy_quote_asset_volume", pa.float64()),
            pa.field("ignore", pa.string())
        ])

    def create_record_batches(self):

        for batch_index, column_data in enumerate(self.column_data):

            # Create RecordBatch using inferred data types
            batch = pa.RecordBatch.from_pydict(column_data)

            # Cast RecordBatch to explicit schema
            batch = batch.cast(self.column_data_schema)

            print(
                f"Processing API Batch {batch_index + 1} "
                f"({batch.num_rows} rows)"
            )

            yield batch

    def create_batch_reader(self):

        self.reader = pa.RecordBatchReader.from_batches(
            self.column_data_schema,
            self.create_record_batches()
        )

    def write_parquet_dataset(self):

        ds.write_dataset(
            data=self.reader,
            base_dir=str(self.output_dir),
            format="parquet",
            partitioning=["symbol"],
            min_rows_per_group=10000,
            max_rows_per_group=10000,
            existing_data_behavior="overwrite_or_ignore"
        )
