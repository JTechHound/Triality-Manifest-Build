"""Unified Triality Pipeline (UTP) - I/O Layer: Archive Engines.

Hot -> warm -> cold telemetry lifecycle:
  DataManagementPlanArchiveEngine  compacts hot-tier CSV series into
                                   Snappy-compressed Parquet in the warm tier,
                                   preserving `# key: value` header metadata.
  CloudArchiveStorageManager       streams warm Parquet blocks to AWS S3
                                   (Glacier storage class) as the cold tier.

Provenance: ported 2026-10-05 from the UTP v5.2 gap pack
(`pipeline_unified.py`, utp-v5 branch of Triality-Pipeline-), which was the
only copy in existence and lived outside any repo's import path.

[CORRECTED] The original built boto3.client('s3') eagerly in __init__,
which raised on credential-less machines at construction time. The client is
now built lazily on first upload, so the nightly cron job idles cleanly
without AWS credentials.
"""
import os

import pandas as _pd
import pyarrow as _pa
import pyarrow.parquet as _pq


class DataManagementPlanArchiveEngine:
    def __init__(self, hot_dir="./hot_tier", warm_dir="./warm_dir"):
        self.hot_dir = hot_dir
        self.warm_dir = warm_dir
        # Strict type-safe schema mapping for telemetry series.
        self.schema = _pa.schema([
            ('t', _pa.float64()), ('radius_r', _pa.float32()),
            ('sigma', _pa.float32()), ('error_logical', _pa.float32()),
            ('quantum_discord', _pa.float32()), ('entropy_s_vn', _pa.float32())])
        os.makedirs(self.hot_dir, exist_ok=True)
        os.makedirs(self.warm_dir, exist_ok=True)

    def extract_header_metadata(self, csv_filepath):
        """Reads `# key: value` header lines into a metadata dict."""
        metadata = {}
        with open(csv_filepath, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    cleaned = line.strip("# \n")
                    if ":" in cleaned:
                        k, v = cleaned.split(":", 1)
                        metadata[k.strip().lower().replace(" ", "_")] = v.strip()
                else:
                    break
        return metadata

    def archive_csv_to_parquet(self, csv_filename):
        """Converts a hot-tier CSV series into compressed warm-tier Parquet.

        Returns True on success, False if the hot file does not exist.
        """
        hot_path = os.path.join(self.hot_dir, csv_filename)
        if not os.path.exists(hot_path):
            return False
        extracted_meta = self.extract_header_metadata(hot_path)
        df = _pd.read_csv(hot_path, comment='#')
        arrow_table = _pa.Table.from_pandas(df, schema=self.schema,
                                            preserve_index=False)
        existing_meta = arrow_table.schema.metadata or {}
        combined_meta = {**existing_meta,
                         **{k.encode('utf-8'): v.encode('utf-8')
                            for k, v in extracted_meta.items()}}
        arrow_table = arrow_table.replace_schema_metadata(combined_meta)
        parquet_filename = csv_filename.replace(".csv", ".parquet")
        warm_path = os.path.join(self.warm_dir, parquet_filename)
        _pq.write_table(arrow_table, warm_path, compression='SNAPPY')
        os.remove(hot_path)  # compacted: safe removal from the hot tier
        return True


class CloudArchiveStorageManager:
    def __init__(self, bucket_name="triality-pipeline-telemetry-archive"):
        self.bucket_name = bucket_name
        self._s3_client = None  # lazy: built on first upload, not here

    def _client(self):
        import boto3
        if self._s3_client is None:
            self._s3_client = boto3.client('s3')
        return self._s3_client

    def upload_parquet_to_cold_archive(self, local_filepath,
                                       cloud_storage_class="GLACIER"):
        """Streams a warm Parquet block into AWS cold storage.

        Returns True on success, False on missing file or AWS failure.
        Raises no credentials error at construction time: without AWS
        credentials the failure surfaces here, at upload time.
        """
        from botocore.exceptions import NoCredentialsError, ClientError
        if not os.path.exists(local_filepath):
            return False
        filename = os.path.basename(local_filepath)
        try:
            self._client().upload_file(
                Filename=local_filepath,
                Bucket=self.bucket_name,
                Key=filename, ExtraArgs={
                    'StorageClass': cloud_storage_class,
                    'Metadata': {'provenance': 'utp_manifest_build',
                                 'data_type': 'columnar_parquet_telemetry'}})
            return True
        except (NoCredentialsError, ClientError) as e:
            print(f"[ARCHIVE] Cold-tier upload failed: {e}")
            return False
