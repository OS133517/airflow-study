from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

def get_file_path(**op_kwargs):

    connection=BaseHook.get_connection(op_kwargs['conn_id'])
    return connection.description

def get_host_name(**context):

    dag_run = context['dag_run']
    return dag_run.conf.get('host_name')

default_args = {
    'start_date':datetime(2023, 1, 1)
}

my_macro_var = {"ipadd" : '{{.NetworkSettings.IPAddress}}'}

with DAG(dag_id='docker_dynamic_test_dag', tags=["docker"], default_args=default_args, schedule_interval='@once', catchup=False, user_defined_macros=my_macro_var) as dag:

    # docker ps -f name=vm -l 이렇게 하면 이름에 vm 들어가는 거 중에서 가장 최신 것만 나오긴하는데...
    
    gVarTest=1
    
    @task
    def test(**context):
        print(gVarTest)
        gVarTest=context['dag_run'].conf.get('number')
        print(gVarTest)

    @task
    def dynamic_test(**context):

        dag_run = context['dag_run']
        dynamic_con = []
        for number in range(1, 1 + dag_run.conf.get('number')):
            dynamic_command='docker run -it -d --name ' + dag_run.conf.get('name') + str(number) + ' -p ' + str(int(dag_run.conf.get('startPort')) + number) + ':80 rastasheep/ubuntu-sshd:18.04'
            tasks=BashOperator(
                task_id='dynamic_task' + str(number),
                bash_command=dynamic_command
            )

             
    test() >> dynamic_test()

