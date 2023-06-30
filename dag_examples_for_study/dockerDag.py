from datetime import datetime
from airflow import DAG
# from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator

default_args = {
    'start_date':datetime(2023, 1, 1)
}

my_macro_var = {"ipadd" : '{{.NetworkSettings.IPAddress}}'}

with DAG(dag_id='docker_sample_dag', default_args=default_args, schedule_interval='@once', catchup=False, user_defined_macros=my_macro_var) as dag:

    docker_task=BashOperator(
       task_id='docker_task',
       bash_command='docker run -it -d --name vm3 -p 8083:80 rastasheep/ubuntu-sshd:18.04'
    )

    docker_task2=BashOperator(
        task_id='docker_task2',
        bash_command='docker inspect -f "{{ipadd}}" vm3',
        do_xcom_push=True
    )

    docker_task3=BashOperator(
        task_id='docker_task3',
        bash_command='echo {{ti.xcom_pull(task_ids="docker_task2")}}'
    )

    docker_task >> docker_task2 >> docker_task3
