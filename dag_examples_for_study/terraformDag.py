from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import json


def get_configs(**context):
    dag_run = context['dag_run']

    return json.dumps(dag_run.conf)


# def print_callable(**op_kwargs):
#    print(op_kwargs['configs'])

default_args = {
    'start_date': datetime(2023, 1, 1)
}

with DAG(
    dag_id='terraform_dag',
    tags=["terraform"],
    default_args=default_args,
    schedule_interval='@once',
    catchup=False) as dag:

    t3 = BashOperator(
        task_id="terraform_init",
        bash_command="pwd",
        cwd="/root/terraform"
    )

    t1 = PythonOperator(
        task_id="get_configs_for_tf_vars",
        python_callable=get_configs,
        provide_context=True
    )

    t2 = BashOperator(
        task_id="make_tf_vars_json",
        bash_command="echo $configs > /root/terraform/tf-vars.json",
        env={"configs": "{{ti.xcom_pull(task_ids='get_configs_for_tf_vars')}}"}
    )

    t4 = BashOperator(
        task_id="terraform_plan_with_vars",
        bash_command="terraform plan -var-file='/root/terraform/tf-vars.json'",
        cwd="/root/terraform"
    )

    t5 = BashOperator(
        task_id="terraform_apply_with_vars",
        bash_command="terraform apply -var-file='/root/terraform/tf-vars.json' -auto-approve",
        cwd="/root/terraform"
    )

    t6 = BashOperator(
        task_id="add_ec2_public_ip_to_ansible_inventory",
        bash_command="""
            terraform output -raw public_ip >> /etc/ansible/hosts
            && echo -e '\n' >> /etc/ansible/hosts
        """,
        cwd="/root/terraform"
    )

    t7 = BashOperator(
        task_id="add_to_known_hosts",
        bash_command="ansible-playbook /etc/ansible/playbook/auto_pass.yaml -i /etc/ansible/hosts"
    )

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7
