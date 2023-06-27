from datetime import datetime
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator

default_args = {
    "start_date" : datetime(2023, 1, 1)
}

practiceDag = DAG(
    dag_id="practiceDag2",
    schedule_interval="@once",
    default_args=default_args,
    tags=["practice"],
    catchup=False
)

task4 = SqliteOperator(
    task_id="task4",
    # 메타데이터가 쌓이는 DB 커넥션은 설정파일에서 세팅을 해줄 수 있지만
    # task에서 DB에 뭔갈 할 필요가 있을 땐 따로 컨넥션을 지정해줘야 사용할 수 있다.
    # 커넥션은 웹서버나 CLI창 모두에서 관리할 수 있다.
    sqlite_conn_id="db_sqlite",
    sql="""
        CREATE TABLE IF NOT EXISTS example_table(
            title TEXT
        )
    """,
    # Dag를 정의할 때 with문을 사용하지 않고 생성자로 정의할 경우,
    # operator에 꼭 어떤 dag를 참조하는지 명시해줘야 airflow에서 task를 인식할 수 있다.
    dag=practiceDag
)

letters = ['a', 'b', 'c']

# 이렇게 for 문으로 중복되는 task들의 경우 동적으로 생성할 수 있다.
for letter in letters:
    tasks = BashOperator(
        task_id=letter,
        bash_command="echo 'this is task '" + letter,
        dag=practiceDag
    )
    # 이렇게 for문 안에서 관계를 정의해야 task4가 끝나고 task a, b, c 모두 연결된다.
    # >>, << 외에 이러한 함수들을 사용해 관계를 정의할 수 있다.
    task4.set_downstream([tasks])

# 이렇게 for문 밖에서 관계를 정의할 경우 마지막 task만 연결됨
# task4 >> [tasks]

