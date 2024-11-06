from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_stock_data():
    stock_symbol = 'AAPL'
    data = yf.download(stock_symbol, start='2024-01-01', end=datetime.today().strftime('%Y-%m-%d'))
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data.to_csv('/tmp/raw_data.csv')
    logger.info("Data extraction complete and saved to /tmp/raw_data.csv")

def transform_data():
    df = pd.read_csv('/tmp/raw_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Moving_Avg'] = df['Close'].rolling(window=5).mean()
    df['Exp_Moving_Avg'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['Daily_Return'] = df['Close'].pct_change()
    df = df[['Date', 'Close', 'Moving_Avg', 'Exp_Moving_Avg', 'Daily_Return']].dropna()
    df.to_csv('/tmp/transformed_data.csv', index=False)
    logger.info("Data transformation complete and saved to /tmp/transformed_data.csv")

def load_data():
    df = pd.read_csv('/tmp/transformed_data.csv')
    df['Pct_Change'] = df['Close'].pct_change() * 100
    df['Cumulative_Return'] = (1 + df['Pct_Change'] / 100).cumprod() - 1
    logger.info("Loaded data with percentage change and cumulative return:")
    logger.info(df.head(10).to_string())

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'stock_etl_dag',
    default_args=default_args,
    description='A more complex ETL pipeline for stock prices',
    schedule_interval='0 12 * * 1-5',
    start_date=datetime(2024, 11, 5, 10),
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_stock_data,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    extract_task >> transform_task >> load_task