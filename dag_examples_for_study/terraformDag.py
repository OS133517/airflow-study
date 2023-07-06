from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import json

def get_configs(**context):

    dag_run = context['dag_run']

    # 파이썬의 dict 자료형도 json과 같은 형식이라 그냥 바로 주면 될 줄 알았는데 dict 자료형의 경우 큰따옴표가 아닌 작은 따옴표로 출력되서
    # json 으로 인식하지 못한다. 그래서 dict형을 json형식으로 변환
    return json.dumps(dag_run.conf)

default_args = {
    'start_date':datetime(2023, 1, 1)
}

my_macro_var = {"ipadd" : '{{.NetworkSettings.IPAddress}}'}

with DAG(
    dag_id='terraform_dag', 
    tags=["terraform"], 
    default_args=default_args, 
    schedule_interval='@once', 
    catchup=False, 
    user_defined_macros=my_macro_var) as dag:

    t1=PythonOperator(
        task_id="get_configs_for_tf_vars",
        python_callable=get_configs,
        provide_context=True
    )

    t2=BashOperator(
        task_id="make_tf_vars_json",
        # 일단은 >> 를 하면 이미 존재하는 내용에 추가하기 때문에 > 로 덮어씌어지게 했음
        bash_command="echo $configs > /root/terraform/tf-vars.json",
        env={"configs":"{{ti.xcom_pull(task_ids='get_configs_for_tf_vars')}}"}
    )
    
    t3=BashOperator(
        task_id="terraform_init",
        bash_command="pwd",
        # 디렉토리에 따라 테라폼은 tf 파일을 인식하는 것 같아서 bash command를 실행할 경로를 지정해줌
        cwd="/root/terraform"
    )
    
    t4=BashOperator(
        task_id="terraform_plan_with_vars",
        # 커맨드에 직접 -var="변수=값" 이렇게 주면서 실행할 수도 있는데 왠지 인식을 못해서 이렇게 json파일을 인식해서 실행하도록 했음
        bash_command="terraform plan -var-file='/root/terraform/tf-vars.json'",
        cwd="/root/terraform"
    )

    t5=BashOperator(
        task_id="terraform_apply_with_vars",
        # apply를 할 때도 변수 파일을 지정해주고 airflow로 실행할 경우 yes를 칠 수 없기 때문에 -auto-approve 옵션을 주면서 실행
        bash_command="terraform apply -var-file='/root/terraform/tf-vars.json' -auto-approve",
        cwd="/root/terraform"
    )

    t1 >> t2 >> t3 >> t4 >> t5