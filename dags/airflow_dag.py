# dags/arbuz_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import pandas as pd
import sys
import os

sys.path.insert(0, '/opt/airflow/src')

from scraper import scrape_arbuz
from cleaner import clean_data
from loader import load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_task(**context) -> int:
    logger.info("scraping started")
    
    try:
        products = scrape_arbuz(max_products=150) 
        
        if not products:
            raise ValueError("no products scraped")
        
        # Сохраняем данные в XCom
        context['task_instance'].xcom_push(key='raw_data', value=products)
        logger.info(f"scraped {len(products)} products")
        return len(products)
        
    except Exception as e:
        logger.error(f"scraping failed: {e}")
        raise


def clean_task(**context) -> int:
    logger.info("cleaning started")
    
    try:
        raw_data = context['task_instance'].xcom_pull(key='raw_data', task_ids='scrape')
        
        if not raw_data:
            raise ValueError("no data parsed")
        
        df = clean_data(raw_data)
        
        if len(df) < 10:  
            raise ValueError(f"little rows amount: {len(df)}")
        
        cleaned_records = df.to_dict('records')
        context['task_instance'].xcom_push(key='cleaned_data', value=cleaned_records)
        logger.info(f"cleaned {len(df)} rows")
        return len(df)
        
    except Exception as e:
        logger.error(f"cleaning failed: {e}")
        raise


def load_task(**context) -> int:
    logger.info("loading started")
    
    try:
        cleaned_data = context['task_instance'].xcom_pull(key='cleaned_data', task_ids='clean')
        
        if not cleaned_data:
            raise ValueError("no cleaned data")
        
        df = pd.DataFrame(cleaned_data)
        rows_loaded = load_data(df)
        
        logger.info(f"loaded {rows_loaded} rows")
        return rows_loaded
        
    except Exception as e:
        logger.error(f"loading failed: {e}")
        raise


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'execution_timeout': timedelta(hours=1), 
}

with DAG(
    dag_id='arbuz_pipeline',
    default_args=default_args,
    description='parsing Arbuz.kz',
    schedule='0 4 * * *',  
    catchup=False,
    tags=['scraper', 'arbuz', 'etl'],
    max_active_runs=1,
) as dag:

    scrape = PythonOperator(
        task_id='scrape',
        python_callable=scrape_task,
        provide_context=True,
    )

    clean = PythonOperator(
        task_id='clean',
        python_callable=clean_task,
        provide_context=True,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_task,
        provide_context=True,
    )

    scrape >> clean >> load