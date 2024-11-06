from sqlalchemy import create_engine
import pandas as pd

# Define the connection URI
DATABASE_URI = "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Query data from the processed_data table to verify
query = "SELECT * FROM processed_data LIMIT 5;"

try:
    df = pd.read_sql(query, engine)
    print("Data in processed_data table:")
    print(df)
except Exception as e:
    print("Error accessing database:", e)