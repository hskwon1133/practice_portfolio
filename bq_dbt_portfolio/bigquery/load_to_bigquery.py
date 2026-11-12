"""
load_to_bigquery.py
---------------------------------------------------------------
PostgreSQL 포트폴리오 프로젝트에서 생성한 synthetic CSV
(sales_kpi_daily, search_funnel_daily, keyword_dim)를
BigQuery raw 데이터셋으로 적재합니다.

사전 준비:
  1. GCP 프로젝트 생성 (BigQuery Sandbox 무료 티어 가능 - 카드 등록 불필요)
  2. gcloud auth application-default login   (또는 서비스 계정 키 사용)
  3. pip install google-cloud-bigquery --break-system-packages
  4. raw_schema_bigquery.sql 로 raw 데이터셋/테이블 먼저 생성

사용법:
  python load_to_bigquery.py --project <GCP_PROJECT_ID>
---------------------------------------------------------------
"""

import argparse
from pathlib import Path

from google.cloud import bigquery

TABLE_CONFIG = {
    "sales_kpi_daily": {
        "file": "sales_kpi_daily.csv",   # export_to_postgres.py 와 동일 소스 CSV 재사용
        "date_cols": ["date"],
    },
    "search_funnel_daily": {
        "file": "search_funnel_daily.csv",
        "date_cols": ["date"],
    },
    "keyword_dim": {
        "file": "keyword_dim.csv",
        "date_cols": [],
    },
}


def load_table(client: bigquery.Client, project: str, table_name: str, csv_path: Path):
    table_id = f"{project}.raw.{table_name}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema_update_options=[],
    )
    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    job.result()  # 완료 대기
    table = client.get_table(table_id)
    print(f"  -> {table_id}: {table.num_rows:,}행 적재 완료")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="GCP 프로젝트 ID")
    parser.add_argument("--data-dir", default="../kpi_data", help="CSV 파일이 있는 디렉토리")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    data_dir = Path(args.data_dir)

    print(f"BigQuery 프로젝트: {args.project}")
    print("raw 데이터셋에 적재를 시작합니다 (스키마는 raw_schema_bigquery.sql로 사전 생성 필요)\n")

    for table_name, cfg in TABLE_CONFIG.items():
        csv_path = data_dir / cfg["file"]
        if not csv_path.exists():
            print(f"  [SKIP] {csv_path} 파일이 없습니다")
            continue
        load_table(client, args.project, table_name, csv_path)

    print("\n적재 완료. 검증 쿼리:")
    print(f"  SELECT COUNT(*) FROM `{args.project}.raw.sales_kpi_daily`")
    print(f"  SELECT COUNT(*) FROM `{args.project}.raw.search_funnel_daily`")


if __name__ == "__main__":
    main()
