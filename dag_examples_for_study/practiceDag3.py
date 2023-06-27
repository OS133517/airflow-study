from datetime import datetime
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.configuration import conf

default_args = {
    "start_date" : datetime(2023, 1, 1)
}

myExecutor = conf.get_mandatory_value("core", "EXECUTOR")

practiceDag = DAG(
    dag_id="practiceDag3",
    schedule_interval="@once",
    default_args=default_args,
    tags=["another_practice"],
    catchup=False
)

# Airflow의 경우 jinja2 template을 내장하고 있기 때문에 이렇게 동적으로 생성할 수 도 있다.
# 현재 예제에서 사용하고 있는 변수들은 모두 기본으로 내장되어있는 변수들이며 직접 정의해두고 사용할 수도 있다.
task5 = BashOperator(
    dag=practiceDag,
    bash_command="echo 'this belongs to dag({{dag.dag_id}})'",
    task_id="task5"
)

task6 = BashOperator(
    dag=practiceDag,
    bash_command="echo 'this dag was executed on {{ds}}'",
    task_id="task6"
)

task7 = BashOperator(
    dag=practiceDag,
    bash_command="echo 'my executor is '" + myExecutor,
    task_id="task7"
)

task8 = BashOperator(
    dag=practiceDag,
    bash_command="echo 'data interval starts on {{ data_interval_start }}'",
    task_id="task8"
)

# 한번에 여러개의 task들을 병렬적으로 수행하고 싶을 경우 이처럼 리스트 형태로 주면 된다.
task5 >> [task6, task7] >> task8