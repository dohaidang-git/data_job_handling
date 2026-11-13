import hashlib
import os 
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import URL

from crawler.topcv_crawler import get_job_id

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

CSV_PATH = ROOT / "dataset" / "data_cleaned.csv"
TOPCV_PATH = ROOT / "dataset" / f"date={datetime.now().strftime('%Y-%m-%d')}" / "topcv_cleaned.csv"

def normalize_link(link):
    if pd.isna(link) or not str(link).strip():
        return None

    parts = urlsplit(str(link).strip())

    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

def make_csv_key(link):
    normalized_link = normalize_link(link)

    if normalized_link is None:
        return None

    link_hash = hashlib.sha256(
        normalized_link.encode("utf-8")
    ).hexdigest()

    return f"csv_{link_hash}"


def make_topcv_key(link):
    job_id = get_job_id(link)

    if job_id is None:
        return None

    return f"topcv_{job_id}"


def insert_without_duplicates(table, connection, keys, data_iter):

    rows = [dict(zip(keys, row)) for row in data_iter]

    if not rows:
        return 0

    statement = insert(table.table).values(rows)
    statement = statement.on_conflict_do_nothing(
        index_elements=["job_key"]
    )

    result = connection.execute(statement)
    return result.rowcount

def import_jobs(df, engine, table_name="jobs"):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        method=insert_without_duplicates,
        chunksize=500,
    )

def main():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ["DB_NAME"],
    )

    engine = create_engine(url)

    try:
        df_csv = pd.read_csv(CSV_PATH)
        df_csv["job_key"] = df_csv["link_description"].apply(make_csv_key)

        df_topcv = pd.read_csv(TOPCV_PATH)
        df_topcv["job_key"] = df_topcv["link_description"].apply(
            make_topcv_key
        )

        df = pd.concat([df_csv, df_topcv], ignore_index=True)

        missing_keys = df[df["job_key"].isna()]
        print(f"Số dòng không có job_key: {len(missing_keys)}")

        # Chỉ import những dòng có thể nhận diện.
        df = df[df["job_key"].notna()]
        df = df.drop_duplicates(subset=["job_key"])

        import_jobs(df, engine)

        print(f"Đã xử lý {len(df)} dòng có job_key hợp lệ.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()