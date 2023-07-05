from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime

def generate_tasks(**kwargs):
    number = int(kwargs["number"])
    tasks = []

    for i in range(1, number + 1):
        task = EmptyOperator(task_id='task' + str(i), dag=dag)
        tasks.append(task)

    return {"tasks" : tasks}

dag = DAG(
    dag_id='dynamic_task_creation',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None
)

generate_tasks=PythonOperator(
    task_id="gen_task",
    python_callable=generate_tasks,
    op_kwargs={"number":"{{dag_run.conf.get('number')}}"},
    dag=dag
)


start_task = EmptyOperator(task_id='start_task', dag=dag)
end_task = EmptyOperator(task_id='end_task', dag=dag)

start_task >> generate_tasks >> end_task
