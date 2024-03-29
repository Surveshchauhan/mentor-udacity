from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2018, 11, 1 ),
    'end_date': datetime(2018, 11, 23),
    'depends_on_past': False,
    #'retries': 0,
    #'retry_delay': timedelta(minutes=5),
    #'email_on_retry': False,
    'catchup': False}

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 0 * * *'
)

start_operator = DummyOperator(
    task_id='Begin_execution', 
    dag=dag
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Staging_events',
    table='Staging_events',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="log_data",
    file_format="'s3://udacity-dend/log_json_path.json'",
    provide_context=True,
    execution_date='start_date'
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Staging_songs',
    table='Staging_songs',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="song_data/A/A/A",
    file_format="'auto'",
    provide_context=True
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    redshift_conn_id="redshift",
    fact_table='songplays',
    source_tbl_query=SqlQueries.songplay_table_insert,
    aws_credentials="aws_credentials",
    dag=dag    
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    redshift_conn_id="redshift",
    dim_table='users',
    source_tbl_query=SqlQueries.user_table_insert,
    aws_credentials="aws_credentials",
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    redshift_conn_id="redshift",
    dim_table='songs',
    source_tbl_query=SqlQueries.song_table_insert,
    aws_credentials="aws_credentials",
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    redshift_conn_id="redshift",
    dim_table='artists',
    source_tbl_query=SqlQueries.artist_table_insert,
    aws_credentials="aws_credentials",
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    redshift_conn_id="redshift",
    dim_table='time',
    source_tbl_query=SqlQueries.time_table_insert,
    aws_credentials="aws_credentials",
    dag=dag
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    redshift_conn_id="redshift",
    aws_credentials="aws_credentials",
    dag=dag
)

end_operator = DummyOperator(
    task_id='Stop_execution',  
    dag=dag
)

start_operator>>[stage_events_to_redshift, stage_songs_to_redshift]
[stage_events_to_redshift,stage_songs_to_redshift]>>load_songplays_table
load_songplays_table>>[load_song_dimension_table, load_user_dimension_table, load_artist_dimension_table, load_time_dimension_table]
[load_song_dimension_table, load_user_dimension_table, load_artist_dimension_table, load_time_dimension_table] >>run_quality_checks
run_quality_checks>>end_operator

