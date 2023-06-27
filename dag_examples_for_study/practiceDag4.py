from datetime import datetime
from airflow import DAG

from airflow.decorators import dag, task

default_args = {
    "start_date" : datetime(2023, 1, 1)
}

@dag(
    dag_id="practiceDag4",
    schedule_interval="@once",
    default_args=default_args,
    tags=["another_practice"],
    catchup=False
)
def practice_dag():

    # 아래와 같이 task 데코레이터를 사용할 경우 내부에서 pythonOperator를 사용한다.
    @task(task_id="task9")
    def practice_task():
        return 'decarator example'

    # task 관계 설정
    practice_task()

dag = practice_dag()
