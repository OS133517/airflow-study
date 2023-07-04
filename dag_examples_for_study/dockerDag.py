from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

# 파이썬 오퍼레이터의 경우 호출하는 파이썬 콜러블에 주는 매개변수를 오퍼레이터를 생성할 때 옵션으로 줄 수 있다.
# op_kwargs는 dict 형, op_args는 리스트이며 받을 때는 아래와 같이 사용하면 된다.
def get_file_path(**op_kwargs):
    # 이렇게 BaseHook.get_connection을 하면 웹서버나 CLI 커맨드로 저장한 커넥션을 id로 갖고 올 수 있다.
    # 현재 예제에서는 편의를 위해 description에 파일 경로를 넣어놔서 description을 return한다.
    connection=BaseHook.get_connection(op_kwargs['conn_id'])
    return connection.description

# 웹 또는 CLI창에서 dag를 트리거할 경우 json형태의 값을 주면서 시작할 수 있는데 Operator를 생성할 때 옵션으로 provide_context=True를 줄 경우
# 파이썬 콜러블에서 **context를 받아 트리거할 때 준 json 값을 사용해 value값을 꺼내 쓸 수 있다. 옵션도 주지않고 context도 받지 않을 경우
# dag_run을 인식하지 못한다.
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
        # 이렇게 env에 키:밸류로 값을 지정할 경우 bash_command에서 $key값 이렇게 사용할 수 있다.
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}', "port":'{{dag_run.conf["port"] if dag_run else ""}}'}
    )

    docker_inspect_task=BashOperator(
        task_id='docker_inspect_task',
        bash_command='docker inspect -f "{{ipadd}}" $dName',
        env={"dName":'{{dag_run.conf["name"] if dag_run else ""}}'},
        # 배쉬 오퍼레이터는 이 옵션에 True 값을 줘야 xcom에 결과가 들어가진다.
        do_xcom_push=True
    )

    get_hosts=PythonOperator(
        task_id='get_hosts_task',
        python_callable=get_host_name,
        # 밖에서 dag_run에서 값을 꺼내쓰기 위해 줘야하는 옵션
        provide_context=True
    )

    get_inventory_path=PythonOperator(
        task_id='get_inventory_task',
        python_callable=get_file_path,
        # 호출하는 파이썬 콜러블에 주는 매개변수
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
