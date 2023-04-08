import argparse
import time
import pandas as pd
from sqlalchemy import create_engine


def main(params):
    df_iter = pd.read_csv(params.path, iterator=True, chunksize=100000)
    engine = create_engine(
        f"postgresql://{params.user}:{params.password}@localhost:5432/{params.db}"
    )

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name="yellow_taxi_data", con=engine, if_exists="replace")

    df.to_sql(name="yellow_taxi_data", con=engine, if_exists="append")

    while True:
        try:
            t_start = time.time()

            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name="yellow_taxi_data", con=engine, if_exists="append")
            t_end = time.time()
            print(f"Inserted 100000 rows, took {t_end - t_start} seconds")
        except StopIteration:
            print("Finished ingesting data")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")

    parser.add_argument("--path", required=True, help="Path to csv file")
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--user", help="Postgres user", default="postgres")
    parser.add_argument("--password", help="Postgres password", default="postgres")

    args = parser.parse_args()

    main(args)
