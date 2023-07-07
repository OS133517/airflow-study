from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook

def get_file_path(**op_kwargs):
    connection = BaseHook.get_connection(op_kwargs['conn_id'])
    return connection.description


def get_host_name(**context):
    dag_run = context['dag_run']
    return dag_run.conf.get('host_name')


default_args = {
    'start_date': datetime(2023, 1, 1)
}

my_macro_var = {"ipadd": '{{.NetworkSettings.IPAddress}}'}

with DAG(dag_id='docker_dynamic_test_dag', tags=["docker"], default_args=default_args,
         schedule_interval='@once', catchup=False, user_defined_macros=my_macro_var) as dag:
    @task
    def test(**context):
        return context['dag_run'].conf.get('number')


    @task
    def dynamic_test(**context):
        dag_run = context['dag_run']
        number = dag_run.conf.get('number')
        name = dag_run.conf.get('name')
        startPort = dag_run.conf.get('startPort')

        dynamic_commands = []

        for number in range(1, 1 + number):
            dynamic_command = 'docker run -it -d --name ' + name + str(number) + ' -p ' + str(
                int(dag_run.conf.get('startPort')) + number) + ':80 rastasheep/ubuntu-sshd:18.04'
            dynamic_commands.append(dynamic_command)

        return dynamic_commands


    BashOperator.partial(task_id="test_bash").expand(bash_command=dynamic_test())
