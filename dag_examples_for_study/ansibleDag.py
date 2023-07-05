from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.decorators import task

def get_connection_host(**op_kwargs):
        # 이렇게 BaseHook.get_connection을 하면 웹서버나 CLI 커맨드로 저장한 커넥션을 id로 갖고 올 수 있다.
        # 현재 예제에서는 편의를 위해 description에 파일 경로를 넣어놔서 description을 return한다.
        connection=BaseHook.get_connection(op_kwargs['conn_id'])
        return {"host":connection.host, "description":connection.description}

def get_host_name(**context):
        dag_run = context['dag_run']
        return dag_run.conf.get('host_name')

default_args={
        "start_date":datetime(2023, 1, 1)
}

ansible_test_dag=DAG(
        dag_id="ansible_test_dag",
        schedule_interval="@once",
        default_args=default_args,
        # 태그를 설정할 땐 이렇게 꼭 리스트 형태로 줘야한다. 여러개를 줄 수도 있고 리스트로 주지 않고 문자열로 줄 경우 한 글자씩 태그가 생긴다.
        tags=["test"],
        catchup=False
)

get_hosts=PythonOperator(
        task_id='get_hosts_task',
        python_callable=get_host_name,
        provide_context=True,
        dag=ansible_test_dag
)

get_inventory_path=PythonOperator(
        task_id='get_inventory_task',
        python_callable=get_connection_host,
        op_kwargs={"conn_id":"{{ti.xcom_pull(task_ids='get_hosts_task')}}"},
        dag=ansible_test_dag
)

ping_hosts=BashOperator(
        task_id="ping_hosts",
        bash_command="ansible -m ping $host_inventory",
        env={
            'host_inventory':'{{ti.xcom_pull(task_ids="get_inventory_task").host}}'
            },
        dag=ansible_test_dag
)

playbook_task=BashOperator(
        task_id="playbook_task",
        bash_command="ansible-playbook -i $host_inventory $playbook",
        env={
            'host_inventory':'{{ti.xcom_pull(task_ids="get_inventory_task").description}}',
            'playbook':'{{dag_run.conf["playbook"] if dag_run else ""}}'
            },
        dag=ansible_test_dag
)

get_hosts >> get_inventory_path >> ping_hosts >> playbook_task
