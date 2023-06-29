from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.decorators import task


def get_file_path(conn_id):
    # 이렇게 BaseHook.get_connection을 하면 웹서버나 CLI 커맨드로 저장한 커넥션을 id로 갖고 올 수 있다.
    # 현재 예제에서는 편의를 위해 description에 파일 경로를 넣어놔서 description을 return한다.
    connection=BaseHook.get_connection(conn_id)
    return connection.description

default_args={
        "start_date":datetime(2023, 1, 1)
        }

test_dag=DAG(
        dag_id="test_dag",
        schedule_interval="@once",
        default_args=default_args,
        # 태그를 설정할 땐 이렇게 꼭 리스트 형태로 줘야한다. 여러개를 줄 수도 있고 문자열로 줄 경우 한 글자씩 생긴다.
        tags=["test"],
        catchup=False
        )

@task(dag=test_dag)
def inventory_path():
    # 이렇게 task에서 위에 정의한 파이썬 함수를 호출해서 사용할 수도 있다.
    return get_file_path("ansible_inventory")

@task(dag=test_dag)
def ip_address(**context):
    # Airflow는 직접 웹서버나 CLI 커맨드로 dag를 실행(trigger)할 수 있는데, 이 때 json 형태의 값을 줄 수 있다.
    # dag 내에서 받을 땐 이렇게 꺼내 쓸 수 있다. get()의 매개변수가 키 값이다.
    return context['dag_run'].conf.get('ip')

# 같은 dag run의 task들은 서로 데이터를 주고 받을 수 있는데 이 때 사용하는 것이 xcom이다.
# ti 또는 task_instance 둘다 사용 가능하며 파이썬 오퍼레이터의 경우 return 값이 알아서 xcom에 push되며
# 꺼내고 싶을 땐 pull해서 사용하면 된다.
add_host=BashOperator(
        task_id="add_host",
        bash_command="""
        echo {{ti.xcom_pull(task_ids="ip_address")}} >> {{ti.xcom_pull(task_ids="inventory_path")}}
        """,
        dag=test_dag
        )

ping_hosts=BashOperator(
        task_id="ping_hosts",
        bash_command="ansible -m ping all",
        dag=test_dag
        )

# task 데코레이터를 쓸 경우 함수명이 task_id가 되며 task들 간의 관계를 정의할 때 함수명() 이렇게 하면 된다.
inventory_path() >> ip_address() >> add_host >> ping_hosts
