"""
Callbacks d'alerte pour Apache Airflow
Appeles automatiquement en cas de succes, echec ou retry
"""
from datetime import datetime
import logging


def on_failure_callback(context):
    dag = context['dag'].dag_id
    tache = context['task_instance'].task_id
    run_id = context['run_id']
    erreur = str(context.get('exception', 'Inconnue'))
    heure = datetime.now().strftime('%Y-%m-%d %H:%M')
    message = f"""
    ALERTE PIPELINE DATA
    DAG    : {dag}
    Tache  : {tache}
    Run    : {run_id}
    Heure  : {heure}
    Erreur : {erreur}
    """
    logging.error(message)


def on_success_callback(context):
    dag = context['dag'].dag_id
    logging.info(f'SUCCESS - DAG {dag} termine avec succes')


def on_retry_callback(context):
    tache = context['task_instance'].task_id
    essai = context['task_instance'].try_number
    logging.warning(f'RETRY - Tache {tache} - essai {essai}/3')
