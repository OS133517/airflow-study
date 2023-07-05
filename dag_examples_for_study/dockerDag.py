from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

def get_file_path(**op_kwargs):
    # 이렇게 BaseHook.get_connection을 하면 웹서버나 CLI 커맨드로 저장한 커넥션을 id로 갖고 올 수 있다.
    # 현재 예제에서는 편의를 위해 description에 파일 경로를 넣어놔서 description을 return한다.
    connection=BaseHook.get_connection(op_kwargs['conn_id'])
    return connection.description

def get_host_name(**context):
    dag_run = context['dag_run']
    return dag_run.conf.get('host_name')

default_args = {
    'start_date':datetime(2023, 1, 1)
}

my_macro_var = {"ipadd" : '{{.NetworkSettings.IPAddress}}'}

with DAG(dag_id='docker_sample_dag', tags=["docker"], default_args=default_args, schedule_interval='@once', catchup=False, user_defined_macros=my_macro_var) as dag:

    docker_run_task=BashOperator(
        task_id='docker_run_task',
        bash_command='docker run -it -d --name $dName -p $port:80 rastasheep/ubuntu-sshd:18.04',
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}', "port":"{{dag_run.conf['port'] if dag_run else ''}}"}
    )

    docker_inspect_task=BashOperator(
        task_id='docker_inspect_task',
        bash_command='docker inspect -f "{{ipadd}}" $dName',
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}'},
        do_xcom_push=True
    )

    get_hosts=PythonOperator(
        task_id='get_hosts_task',
        python_callable=get_host_name,
        provide_context=True
    )

    get_inventory_path=PythonOperator(
        task_id='get_inventory_task',
        python_callable=get_file_path,
        op_kwargs={"conn_id":"{{ti.xcom_pull(task_ids='get_hosts_task')}}"}
    )

    # @task
    # def inventory_path():
        # 이렇게 task에서 위에 정의한 파이썬 함수를 호출해서 사용할 수도 있다.
    #    return get_file_path({{ti.xcom_pull(task_ids="get_hosts")}})

    add_host=BashOperator(
        task_id="add_host",
        bash_command="""
        echo {{task_instance.xcom_pull(task_ids="docker_inspect_task")}} >> {{ti.xcom_pull(task_ids="get_inventory_task")}}
        """
    )

    docker_run_task >> docker_inspect_task >> get_hosts >> get_inventory_path >> add_host
