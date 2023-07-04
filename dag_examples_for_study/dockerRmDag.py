from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'start_date':datetime(2023, 1, 1)
}

with DAG(dag_id='docker_sample_rm_dag', tags=["docker"], default_args=default_args, schedule_interval='@once', catchup=False) as dag:

    docker_stop_task=BashOperator(
        task_id='docker_stop_task',
        bash_command='docker stop $(docker ps -f name=$dName -q)',
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}'}
    )

    docker_rm_task=BashOperator(
        task_id='docker_rm_task',
        bash_command='docker rm $(docker ps -f name=$dName -aq)',
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}'}
    )

    docker_check_task=BashOperator(
        task_id="docker_check_task",
        bash_command='docker ps -a'
    )

    docker_stop_task >> docker_rm_task >> docker_check_task
