from datetime import datetime
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.smooth import SmoothOperator

default_args = {
    "start_date" : datetime(2023, 1, 1)
}

with DAG(
    dag_id="practiceDag1",
    schedule="@once",
    default_args=default_args,
    tags=["practice"],
    catchup=False
    ) as dag:

    print_hello_task = BashOperator(
        task_id="task1",
        bash_command='echo "hello world!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"'
    )

    print_bye_task = BashOperator(
        task_id="task2",
        bash_command='echo "good bye~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"'
    )

    smooth_task = SmoothOperator(
        task_id="task3"
    )

    print_hello_task >> smooth_task >> print_bye_task
    
