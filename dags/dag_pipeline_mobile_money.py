"""
DAG Airflow — Pipeline ETL Mobile Money CI
Execute quotidiennement à 23h00
5 tâches : extract → clean → load → dbt → report
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
import json
import os

default_args = {
    'owner': 'trinome_data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['equipe@projet.ci'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

def on_failure_callback(context):
    dag = context['dag'].dag_id
    tache = context['task_instance'].task_id
    erreur = str(context.get('exception', 'Inconnue'))
    logging.error(f'ALERTE - DAG: {dag} - Tache: {tache} - Erreur: {erreur}')

def task_extract(**context):
    log = logging.getLogger(__name__)
    log.info('EXTRACT - Demarrage')
    df = pd.read_csv('/data/Data2_transactions_mobile_money_100k.csv',
                     encoding='utf-8', low_memory=False)
    nb = len(df)
    context['ti'].xcom_push(key='nb_brutes', value=nb)
    df.to_parquet('/data/raw/transactions_raw.parquet', index=False)
    log.info(f'EXTRACT - {nb:,} lignes extraites')
    return nb

def task_clean(**context):
    log = logging.getLogger(__name__)
    df = pd.read_parquet('/data/raw/transactions_raw.parquet')
    df = df.replace('', np.nan)
    df['frais_fcfa'] = df['frais_fcfa'].fillna(0).astype(int)
    df['zone_beneficiaire'] = df['zone_beneficiaire'].fillna('Zone inconnue')
    df['id_agent'] = df['id_agent'].fillna('AGT-INCONNU')
    df = df[df['montant_fcfa'] > 0].copy()
    df['date_heure'] = pd.to_datetime(df['date_heure'])
    df['montant_net_fcfa'] = df['montant_fcfa'] - df['frais_fcfa']
    df['heure'] = df['date_heure'].dt.hour
    df['mois'] = df['date_heure'].dt.strftime('%Y-%m')
    nb = len(df)
    context['ti'].xcom_push(key='nb_propres', value=nb)
    df.to_parquet('/data/clean/transactions_clean.parquet', index=False)
    log.info(f'CLEAN - {nb:,} lignes propres')
    return nb

def task_load(**context):
    import sqlalchemy
    log = logging.getLogger(__name__)
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    if not SUPABASE_URL:
        raise ValueError('SUPABASE_URL non definie')
    engine = sqlalchemy.create_engine(SUPABASE_URL)
    df = pd.read_parquet('/data/clean/transactions_clean.parquet')
    chunks = [df[i:i+5000] for i in range(0, len(df), 5000)]
    with engine.connect() as conn:
        for chunk in chunks:
            chunk.to_sql('transactions', conn, if_exists='append',
                         index=False, method='multi', chunksize=500)
        conn.commit()
    log.info(f'LOAD - {len(df):,} lignes chargees')
    engine.dispose()

def task_report(**context):
    log = logging.getLogger(__name__)
    df = pd.read_parquet('/data/clean/transactions_clean.parquet')
    df_s = df[df['statut'] == 'Succès']
    ti = context['ti']
    nb_brutes = ti.xcom_pull(task_ids='extract_csv', key='nb_brutes')
    nb_propres = ti.xcom_pull(task_ids='clean_data', key='nb_propres')
    rapport = {
        'date_generation': str(datetime.now().strftime('%Y-%m-%d %H:%M')),
        'nb_brutes': nb_brutes,
        'nb_propres': nb_propres,
        'nb_aberrations': (nb_brutes or 0) - (nb_propres or 0),
        'volume_total_fcfa': int(df_s['montant_fcfa'].sum()),
        'taux_succes_pct': round(len(df_s)/len(df)*100, 1),
        'montant_moyen_fcfa': int(df_s['montant_fcfa'].mean()),
    }
    os.makedirs('/data/output', exist_ok=True)
    with open('/data/output/rapport_nuit.json', 'w') as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    log.info('RAPPORT - genere')

with DAG(
    dag_id='pipeline_mobile_money_ci',
    default_args=default_args,
    description='ETL Mobile Money CI - quotidien 23h',
    schedule='0 23 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'mobile_money', 'ci'],
    on_failure_callback=on_failure_callback,
) as dag:

    t_extract = PythonOperator(
        task_id='extract_csv',
        python_callable=task_extract,
    )
    t_clean = PythonOperator(
        task_id='clean_data',
        python_callable=task_clean,
    )
    t_load = PythonOperator(
        task_id='load_supabase',
        python_callable=task_load,
    )
    t_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='cd /projet_dbt && dbt run --profiles-dir /home/airflow/.dbt 2>/dev/null || echo "dbt non configure"',
    )
    t_report = PythonOperator(
        task_id='generate_report',
        python_callable=task_report,
    )

    t_extract >> t_clean >> t_load >> t_dbt >> t_report
